# Roadmap

This document captures follow-on work for the Release Delta Records (RDR) repository beyond the v1 scaffold. Items are grouped by what they unblock, not by delivery date. Pick from the top of each section first; deeper items earn their place as the practice matures.

The list is read as guidance, not commitment. Anything here can be reordered, rescoped, or dropped as adoption surfaces needs the speculative list missed. Convert items to GitHub issues at the point of pickup; the roadmap exists to hold the shape of the work, not to coordinate execution against it.

## Adoption infrastructure

Items that make the next team's first delta easier to write and reduce the gap between scaffold and lived practice.

### Worked example: Platform/Enablement
The hardest delta type to declare cleanly because the user is another engineer or team rather than an end customer. Validating the template against a Platform/Enablement release confirms the framework's claim that the same artifact serves all six types. Produces an additional `examples/RD-NNNN-...md` in the same evaluated state as the Growth example.

### Worked examples: the remaining four delta types
Retention/Engagement, Monetization, Experience/Quality, and Risk Reduction each deserve a worked example. Lower priority than Platform because Growth already exists and Platform is the hardest case; the other four are mostly variations that an experienced author can extrapolate from the first two.

### New-delta helper script
A small `scripts/new-delta.sh` that finds the next sequential number, prompts for a slug, copies `templates/minimal.md` to the right location, and opens the file. Removes a small but real friction at the start of writing a delta. Should not enforce additional rules; CI is the enforcement layer.

### Service-repo PR template
A short markdown template that service repositories can copy into `.github/pull_request_template.md` requiring a delta ID reference. Strengthens the cross-repo linkage convention by surfacing the omission at PR-open time rather than at review.

## Reporting

Items that become valuable once the repo accumulates more than a handful of deltas.

### Generated index page
A static index, rebuilt on merge to main, listing every delta with its status, type, owners, declared and evaluated dates, and a link to the file. Unblocks "find me every Growth delta from Q3" without grepping. Could ship as a GitHub Pages site, a generated `INDEX.md`, or both.

### Chain-traversal report
Walk the `related.supersedes` and `related.superseded_by` fields and surface orphans, broken links, and chains that grow beyond a reasonable depth (typically a signal of scope drift). Useful as a weekly or monthly scheduled report.

### Stale-delta report
Identify deltas that have been `proposed` for more than a configured threshold, or `active` past their Horizon. Both states represent process failures the framework cares about; the report is the visibility mechanism that turns implicit drift into explicit work.

### Maturity ladder rollup
Once the repo has enough evaluated deltas, compute the team's position on the RIVER maturity ladder (Deploy, Control, Declare, Prove, Learn) from the artifact corpus. Genuinely speculative as a v2 item because the ladder's empirical calibration is still ahead of the framework. Worth keeping on the list as a marker.

## Schema evolution

Items that strengthen the specification as the practice matures and reveals the limits of v1.

### Cryptographic immutability via declaration_hash
At the moment status flips to `active`, embed a hash of the declaration block in the frontmatter (`declaration_hash: sha256:...`). CI verifies the hash on every read. Defends against history rewrites and provides a portable proof that a declaration was not edited after the fact. Earns its place if the organization needs stronger guarantees than "CI says so."

### Required evaluated date in frontmatter for terminal states
The frontmatter `evaluated:` date is currently informational; the same data is reachable through the git log. If reporting tooling needs the date in the artifact directly, promote it to required when status is `evaluated`, `reversed`, or `abandoned`. Defer until reporting actually needs it.

### Timeline section for actual versus declared rollout
The release delta declares the *planned* progression (5%, 25%, 50%, 100%); the flag platform's audit log holds the *actual* progression (when each stage transitioned, which guardrails fired). A Timeline section captured at evaluation time would put both in the document. Useful but not yet missed.

### Split cohort_definition from cohort_progression
Target Cohort currently carries two distinct things: who is eligible and how exposure progresses. They are coupled in v1 deliberately, because writing them together surfaces dependencies. Split if a real adoption signal shows that the coupling is more cost than benefit.

### Detection-power check for declared magnitudes
A linter that estimates whether the declared cohort size is large enough to detect the declared magnitude at conventional statistical power. Catches "20% lift on a cohort of 80" before the delta is merged. Requires modeling assumptions the framework does not yet specify; deferrable.

## Integration

Items that extend the repo's reach into surrounding systems.

### Live link resolution checks
A scheduled job (not the PR merge gate) that follows the URLs in `links.flags`, `links.experiments`, and `links.dashboards` and reports broken links. Runs nightly or weekly. Out of scope for the merge gate because external API flakiness produces false PR failures.

### Direct API integration with flag and experiment platforms
Fetch actual rollout data from the platform of record and surface it in the generated index or the stale-delta report. Begins the path toward computing the seven metric families automatically. A v2 effort with platform-specific adapters; the file's `links` block already carries the addressing the integration needs.

### RIVER voice prose linter
An optional check that flags em dashes, fragment bullets, and other voice violations against the style guide. Should be advisory rather than blocking; voice is a quality goal, not a correctness boundary.

### Tests for the CI script itself
A small pytest suite covering the validation rules with synthetic inputs. v1 ships with end-to-end scenario testing only; as the rule set grows, unit tests will earn their place.

## Out of scope for now

Decisions made deliberately and not to be re-litigated without new information.

### Co-locating deltas with service code
Considered and rejected. Release Deltas are cross-functional product artifacts, not engineering documentation, and frequently span repositories. Linkage is via delta ID, not filesystem adjacency.

### Switching to a non-Markdown format
Considered and rejected. Markdown's universality is the adoption asset; structural format changes (AsciiDoc, fully structured YAML, custom DSLs) trade portability for elegance the framework does not yet need. Revisit only if v1's prose-plus-frontmatter approach hits a concrete wall.

### Pairing each delta with a separate evaluation file
Considered and rejected. Mutating the original file is simpler, keeps the artifact whole, and the immutability convention plus git history preserves what pairing would protect. Pairing would double the file count without strengthening the commitment.

### CI checks against live platform APIs at PR time
Considered and rejected. External APIs produce flaky CI failures. Resolution and live-data checks belong to scheduled jobs, not to the merge gate.
