#!/usr/bin/env python3
"""Validate Release Delta files in a pull request.

Runs as a GitHub Actions step on PRs touching docs/release-deltas/.
Can also be run locally; set GITHUB_BASE_REF to the branch you are
merging into (defaults to `main`).

Validation rules:
  Format
    - Filename matches RD-NNNN-slug.md.
    - YAML frontmatter is parseable and contains the required fields.
    - Frontmatter `id` matches the filename.
    - `status` is one of the allowed values.
    - `type` is one of the six taxonomy values.
    - `declared` is a YYYY-MM-DD date.
    - `owners` includes product, engineering, and operations.
    - Required body sections are present.
    - `status: superseded` requires `related.superseded_by` to be non-empty.
    - `status: evaluated|reversed|abandoned` requires a non-placeholder Outcome.
    - All entries in `links.{flags,experiments,dashboards}` are valid URLs.
    - `status: evaluated|reversed|superseded` requires at least one flag link.

  Diff (against base ref)
    - New files start at status `proposed`.
    - Status transitions follow the state machine.
    - Once base status is past `proposed`, the four declaration sections
      and the locked frontmatter fields are byte-equal to the base.
    - File deletions and renames are rejected; mark `abandoned` instead.
"""

import os
import re
import sys
import subprocess
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import yaml


DELTAS_DIR = Path("docs/release-deltas")
FILENAME_PATTERN = re.compile(r"^RD-(\d{4})-[a-z0-9-]+\.md$")
URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)

VALID_STATUSES = {
    "proposed", "active", "evaluated", "reversed", "abandoned", "superseded",
}
VALID_TYPES = {
    "growth", "retention", "monetization", "experience", "platform", "risk",
}
LOCKED_STATUSES = VALID_STATUSES - {"proposed"}
EVALUATED_STATUSES = {"evaluated", "reversed", "abandoned"}
REQUIRES_FLAG_LINK = {"evaluated", "reversed", "superseded"}

REQUIRED_FRONTMATTER = {"id", "title", "status", "type", "declared", "owners"}
REQUIRED_OWNERS = {"product", "engineering", "operations"}
LOCKED_FRONTMATTER_FIELDS = ("type", "declared")

IMMUTABLE_SECTIONS = ["Hypothesis", "Success Signal", "Target Cohort", "Horizon"]
REQUIRED_SECTIONS = IMMUTABLE_SECTIONS + ["Outcome"]
LINK_FIELDS = ("flags", "experiments", "dashboards")

PLACEHOLDER_OUTCOMES = {"", "tbd", "n/a"}

VALID_TRANSITIONS = {
    "proposed":   {"active", "abandoned"},
    "active":     {"evaluated", "reversed", "abandoned"},
    "evaluated":  {"superseded"},
    "reversed":   {"superseded"},
    "abandoned":  set(),
    "superseded": set(),
}


# ---------- Parsing helpers ----------

def parse_frontmatter(content):
    """Return (frontmatter_dict, body_string). Raises ValueError on failure."""
    if not content.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    end = content.find("\n---\n", 4)
    if end == -1:
        raise ValueError("frontmatter not closed with ---")
    try:
        fm = yaml.safe_load(content[4:end]) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"YAML parse error: {e}")
    if not isinstance(fm, dict):
        raise ValueError("frontmatter must be a mapping")
    body = content[end + 5:]
    return fm, body


def extract_sections(body):
    """Map H2 section name -> trimmed content body."""
    sections, current, buf = {}, None, []
    for line in body.splitlines():
        m = re.match(r"^## (.+)$", line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current, buf = m.group(1).strip(), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    return sections


def is_placeholder(text):
    stripped = text.strip().lower()
    if stripped in PLACEHOLDER_OUTCOMES:
        return True
    return stripped.startswith("{") and stripped.endswith("}")


# ---------- Format validation ----------

def validate_format(path, content):
    errors = []

    m = FILENAME_PATTERN.match(path.name)
    if not m:
        return ["filename does not match RD-NNNN-slug.md"]
    expected_id = f"RD-{m.group(1)}"

    try:
        fm, body = parse_frontmatter(content)
    except ValueError as e:
        return [f"frontmatter error: {e}"]

    missing = REQUIRED_FRONTMATTER - set(fm.keys())
    if missing:
        errors.append(f"missing required frontmatter fields: {sorted(missing)}")

    if fm.get("id") != expected_id:
        errors.append(
            f"frontmatter id '{fm.get('id')}' does not match filename '{expected_id}'"
        )

    status = fm.get("status")
    if status not in VALID_STATUSES:
        errors.append(
            f"invalid status '{status}'; must be one of {sorted(VALID_STATUSES)}"
        )

    if fm.get("type") not in VALID_TYPES:
        errors.append(
            f"invalid type '{fm.get('type')}'; must be one of {sorted(VALID_TYPES)}"
        )

    if not isinstance(fm.get("declared"), date):
        errors.append("'declared' must be a YYYY-MM-DD date")

    owners = fm.get("owners") or {}
    if not isinstance(owners, dict):
        errors.append("'owners' must be a mapping")
    else:
        missing_owners = REQUIRED_OWNERS - set(owners.keys())
        if missing_owners:
            errors.append(f"owners missing required roles: {sorted(missing_owners)}")
        empty_owners = [r for r in REQUIRED_OWNERS
                        if r in owners and not str(owners[r] or "").strip()]
        if empty_owners:
            errors.append(f"owners has empty values for: {sorted(empty_owners)}")

    sections = extract_sections(body)
    missing_sections = set(REQUIRED_SECTIONS) - set(sections.keys())
    if missing_sections:
        errors.append(f"missing required sections: {sorted(missing_sections)}")

    if status == "superseded":
        sb = (fm.get("related") or {}).get("superseded_by") or []
        if not (isinstance(sb, list) and sb):
            errors.append(
                "status 'superseded' requires related.superseded_by to be a non-empty list"
            )

    if status in EVALUATED_STATUSES:
        outcome = sections.get("Outcome", "")
        if is_placeholder(outcome):
            errors.append(
                f"status '{status}' requires a non-empty, non-placeholder Outcome"
            )

    errors.extend(validate_links(fm))

    return errors


def validate_links(fm):
    errors = []
    links = fm.get("links") or {}
    if not isinstance(links, dict):
        return ["'links' must be a mapping"]

    for field in LINK_FIELDS:
        urls = links.get(field) or []
        if not isinstance(urls, list):
            errors.append(f"'links.{field}' must be a list")
            continue
        for url in urls:
            if not isinstance(url, str) or not URL_PATTERN.match(url):
                errors.append(f"'links.{field}' contains an invalid URL: {url!r}")
                continue
            parsed = urlparse(url)
            if not parsed.netloc:
                errors.append(f"'links.{field}' URL has no host: {url!r}")

    if fm.get("status") in REQUIRES_FLAG_LINK:
        if not (links.get("flags") or []):
            errors.append(
                f"status '{fm.get('status')}' requires at least one entry in links.flags"
            )

    return errors


# ---------- Diff validation ----------

def file_at_ref(path, ref):
    try:
        out = subprocess.run(
            ["git", "show", f"{ref}:{path}"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout
    except subprocess.CalledProcessError:
        return None


def validate_diff(path, new_content, base_ref):
    errors = []
    base_content = file_at_ref(str(path), base_ref)

    if base_content is None:
        try:
            new_fm, _ = parse_frontmatter(new_content)
        except ValueError:
            return errors
        if new_fm.get("status") != "proposed":
            errors.append(
                f"new release delta must start with status 'proposed'; "
                f"got '{new_fm.get('status')}'"
            )
        return errors

    try:
        old_fm, old_body = parse_frontmatter(base_content)
        new_fm, new_body = parse_frontmatter(new_content)
    except ValueError:
        return errors

    old_status, new_status = old_fm.get("status"), new_fm.get("status")
    if old_status != new_status and old_status in VALID_STATUSES:
        allowed = VALID_TRANSITIONS.get(old_status, set())
        if new_status not in allowed:
            allowed_str = sorted(allowed) if allowed else "none (terminal)"
            errors.append(
                f"invalid status transition '{old_status}' -> '{new_status}'; "
                f"allowed from '{old_status}': {allowed_str}"
            )

    if old_status in LOCKED_STATUSES:
        old_sections = extract_sections(old_body)
        new_sections = extract_sections(new_body)
        for name in IMMUTABLE_SECTIONS:
            if old_sections.get(name, "") != new_sections.get(name, ""):
                errors.append(
                    f"section '{name}' is immutable once status is past 'proposed' "
                    f"(base status: '{old_status}'); supersede this delta instead"
                )
        for field in LOCKED_FRONTMATTER_FIELDS:
            if old_fm.get(field) != new_fm.get(field):
                errors.append(
                    f"frontmatter '{field}' is immutable once status is past 'proposed'"
                )

    return errors


# ---------- Change discovery ----------

def changed_delta_paths(base_ref):
    out = subprocess.run(
        ["git", "diff", "--name-status", f"{base_ref}...HEAD"],
        capture_output=True, text=True, check=True,
    )
    changed, removed = [], []
    for line in out.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status = parts[0]
        # Rename: ["R100", "old", "new"]; treat as removal of old.
        if status.startswith("R") and len(parts) >= 3:
            old_path = Path(parts[1])
            new_path = Path(parts[2])
            if _is_delta(old_path) or _is_delta(new_path):
                removed.append(old_path)
            continue
        path = Path(parts[-1])
        if not _is_delta(path):
            continue
        if status.startswith("D"):
            removed.append(path)
        else:
            changed.append(path)
    return changed, removed


def _is_delta(path):
    return (
        path.parent == DELTAS_DIR
        and path.suffix == ".md"
        and path.name != "README.md"
    )


# ---------- Entry point ----------

def main():
    base_ref = os.environ.get("GITHUB_BASE_REF", "main")
    try:
        subprocess.run(
            ["git", "fetch", "--no-tags", "origin", base_ref],
            check=True, capture_output=True,
        )
    except subprocess.CalledProcessError:
        # If origin is not configured (local dev), fall back to the local ref.
        pass
    full_ref = f"origin/{base_ref}"
    if file_at_ref("README.md", full_ref) is None:
        full_ref = base_ref

    changed, removed = changed_delta_paths(full_ref)
    if not changed and not removed:
        print("No release delta changes to validate.")
        return 0

    all_errors = []
    for path in removed:
        all_errors.append((
            path,
            "deleting or renaming a release delta is not allowed; "
            "mark it 'abandoned' instead",
        ))

    for path in changed:
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        for err in validate_format(path, content):
            all_errors.append((path, err))
        for err in validate_diff(path, content, full_ref):
            all_errors.append((path, err))

    if all_errors:
        print(f"Found {len(all_errors)} validation error(s):\n")
        for path, err in all_errors:
            print(f"  {path}: {err}")
        return 1

    print(f"Validated {len(changed)} release delta(s). All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
