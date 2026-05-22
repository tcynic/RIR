# Release Delta Records (RDR)

This repository holds the declared Release Delta Records (RDRs) for {Product}.

A Release Delta is a structured artifact, created before a release begins, that names the type of release, the hypothesis being tested, the success signal that will tell us the hypothesis held, the target cohort, and the horizon by which we expect to know. Release Delta is the unit of analysis in RIVER; team and organization rollups aggregate over deltas, not over deploys, flags, or tickets.

This repository is the source of truth for what we are shipping, why, and how we will know it worked. The framework itself, the metric family definitions, and the maturity ladder live at https://www.river-framework.dev. Read that when you want to know what the framework is. Read this README when you want to write or evaluate a delta.

## Quick start

To write a new Release Delta:

1. Copy `templates/minimal.md` to `docs/release-deltas/RD-NNNN-slug.md`, where `NNNN` is the next sequential number and `slug` is a short dashed-lowercase title.
2. Fill in the YAML frontmatter and the five required sections.
3. Open a pull request. The CI checks will tell you if anything is missing or malformed.
4. Hold a declaration review with the three co-owners. Capture review notes in the Notes section.
5. Merge. Status stays at `proposed` until the rollout actually begins.

If you have not written one before, read `examples/RD-0042-in-product-invites.md` first. It is a fully worked Growth delta through every stage of the lifecycle, and it shows what good answers to the five questions look like, including a realistic mixed-result Outcome.

## Repository layout

```
docs/release-deltas/    Declared deltas, one per file.
templates/               minimal.md and full.md.
examples/                Worked examples by delta type.
.github/scripts/         CI validation script.
.github/workflows/       PR validation workflow.
README.md                This file.
ROADMAP.md               Follow-on work and out-of-scope decisions.
```

Files in `docs/release-deltas/` follow the pattern `RD-NNNN-slug.md`. Numbers are sequential and never reused. The slug is short, dashed, and lowercase; it does not need to capture every nuance of the title.

## What goes in a delta

Every Release Delta answers five questions. They are the floor of the framework, and they are required.

**Type.** One of six values: `growth`, `retention`, `monetization`, `experience`, `platform`, or `risk`. Pick the one that best describes what the release is supposed to move. A Platform release that makes the next five Growth releases faster is a good Platform release; do not retype it as Growth to inflate apparent business impact.

**Hypothesis.** What we believe will happen when the target cohort encounters this release. Stated as a claim, not a question. The Hypothesis is what you actually believe, not what sounds defensible to leadership.

**Success Signal.** The metric, the direction, the magnitude, and the window. One metric per delta. If your release moves multiple metrics, pick the terminal funnel metric and let the decomposition surface in Outcome at evaluation time. Set the magnitude honestly given baseline; a threshold you cannot detect at the declared cohort size is a threshold you have not declared.

**Target Cohort.** Who this is for, and how exposure will progress through them. The progression plan is part of the cohort definition. Name the eligibility criteria, the progression stages (typically `5% → 25% → 50% → 100%` or similar), and the gating condition between stages.

**Horizon.** The date by which we expect to know whether the hypothesis held. The Horizon is a commitment, not an aspiration. A Horizon that arrives and finds the team unable to evaluate is a process failure, not a flexible deadline.

The optional sections (Context, Guardrails, Reversibility, Out of scope, Notes) carry detail that helps reviewers and future readers. They are not required, but a declared delta without Guardrails or Reversibility is a release that has not been thought through operationally, and the declaration review will say so.

## Owners

Every delta has three named owners: product, engineering, and operations. These are roles, not departments. The product owner stewards the Hypothesis and Success Signal. The engineering owner stewards the implementation, the flag, and the rollback mechanism. The operations owner stewards monitoring, guardrails, and incident response during the rollout.

If your team does not have someone playing the operations role for a particular release, name an explicit substitute. Leaving the field empty is not an option; the framework's claim is that release is a cross-functional decision, and the artifact reflects that.

## The lifecycle

```
proposed ──→ active ──→ evaluated ──→ superseded
    │          │
    │          ├──→ reversed ──→ superseded
    │          │
    └──────────┴──→ abandoned (terminal)
```

**proposed.** The delta has been declared and reviewed but the rollout has not begun. Edits are still allowed.

**active.** The rollout has begun. The four declaration sections (Hypothesis, Success Signal, Target Cohort, Horizon) and the frontmatter fields `type` and `declared` are now immutable.

**evaluated.** The Horizon has arrived (or the Success Signal is decisively known) and the Outcome has been written. Terminal except for being superseded by a follow-on delta.

**reversed.** The release was pulled back, by guardrail trigger or manual decision, before completion. Outcome captures what happened and what was learned.

**abandoned.** The release never ran or was canceled before exposure. Terminal.

**superseded.** Replaced by a follow-on delta that takes over the work. The `related.superseded_by` field names the successor.

## What is immutable, and why

Once status is past `proposed`, four sections cannot be edited: Hypothesis, Success Signal, Target Cohort, and Horizon. The frontmatter fields `type` and `declared` are also locked.

The point of the lock is the framework's central operating claim: a declared commitment that can be revised after the fact is not a commitment. Most teams can describe a release in soft language after it ships; few can describe it precisely before. The immutability of the declaration is what produces the discipline that produces the measurement.

If the world genuinely changes (the cohort definition is wrong, the platform shifts, a higher-priority delta makes this one obsolete), the answer is to **supersede**, not to edit. Write a new delta that names this one as `related.supersedes`, and mark this one `superseded` with the new ID in `related.superseded_by`. The history is preserved; the commitment is honored.

CI rejects edits to immutable sections. If you need to make a change, the error message will tell you to supersede.

## Linkage to the seven metric families

Every Release Delta carries a `links` block in the frontmatter pointing at the systems that hold the data the framework needs:

- `links.flags` points at the flag platform of record. This is the source for Exposure, Cohort Progression, Reversal, and (on most platforms) Guardrail metrics.
- `links.experiments` points at the experiment platform when the delta is experiment-linked. This is the source for Outcome Attribution.
- `links.dashboards` points at the dashboard or BI tool tracking the business KPI being moved. This is the source for Impact metrics.

Adoption metrics (first-use, sustained-use, value-realization) need no separate link; the cohort is defined by Target Cohort and the value-realization event is defined by Success Signal.

Links are URLs, not IDs. Humans get a clickable destination; tooling can parse the URL to identify the platform. The schema is tool-neutral by structure: any platform with stable URLs fits.

Links are mutable. Flags get renamed and dashboards move; locking these would generate ceremony without protecting commitment. CI requires that a delta reaching `evaluated`, `reversed`, or `superseded` carry at least one flag link, because the framework cannot compute Exposure, Cohort Progression, Reversal, or Guardrail metrics for a delta without a flag attached.

## Evaluation

When the Horizon arrives, the Outcome must be written. A Release Delta without a substantive Outcome at evaluation time is a process failure that future readers cannot recover from.

A good Outcome does four things: it states whether the hypothesis held at the declared threshold (yes, no, or partial); it decomposes the result so the reader understands what moved and what did not; it names what was learned; and it names follow-up deltas if any. The Outcome section has no required structure beyond "non-empty and not a placeholder," because premature structure forces booleans that miss real findings. See the worked example for what an honest mixed-result Outcome reads like.

Evaluation is not optional and it is not deferrable. A delta whose Horizon has passed without an evaluation is the framework's clearest failure mode, and the maturity ladder will eventually treat un-evaluated deltas as a measurable deficit.

## CI rules

The validation script enforces the following on every pull request:

The filename matches `RD-NNNN-slug.md`. The frontmatter is parseable and contains every required field. The five required sections are present. New files start with status `proposed`. Status transitions follow the state machine; an invalid transition is rejected with the list of allowed transitions for the current status. Once status is past `proposed`, the four declaration sections and the locked frontmatter fields are byte-equal to the base branch. Files cannot be deleted or renamed; an unwanted delta is marked `abandoned`. Status transitions to `evaluated`, `reversed`, or `abandoned` require a non-placeholder Outcome. Status transitions to `superseded` require `related.superseded_by` to be populated. Links are valid URLs. Deltas reaching `evaluated`, `reversed`, or `superseded` have at least one entry in `links.flags`.

The script lives at `.github/scripts/validate_release_deltas.py` and runs via `.github/workflows/validate-release-deltas.yml` on every PR that touches `docs/release-deltas/`. CI does not check that link URLs resolve or that flags still exist in the platform; resolution belongs to a separate scheduled job, not to the merge gate.

To run the validator locally before opening a PR:

```
pip install pyyaml
GITHUB_BASE_REF=main python .github/scripts/validate_release_deltas.py
```

## Cross-referencing with code

This repository is intentionally separate from the service repositories that implement releases. Engineering pull requests in those repos reference the delta ID in their description (`Implements RD-0042` or `Closes RD-0042`), and service repo PR templates can require the reference.

The release delta declares the flag URL in `links.flags`. The engineering PR creates the flag, configures the targeting rule, and updates the delta's `links.flags` if the URL changes. Linkage is bidirectional through the ID, not through filesystem adjacency.

If a single delta ships across multiple services, each service repo PR references the same delta ID. If a single service ships work for multiple deltas, each PR references its own delta. The mapping is many-to-many.

## Common situations

**The rollout percentages need to change mid-flight.** The progression plan is part of Target Cohort, which is immutable. If the plan needs to change because of what you have learned, supersede the delta. If the plan needs to change because of an operational issue (a guardrail tripped and you are pausing), update the flag platform; the delta's progression plan is the *declared* plan, and the flag platform's audit log is the *actual* progression. Both are useful and they answer different questions.

**The release worked but at a lower magnitude than declared.** The hypothesis did not hold at the declared threshold. State that honestly in Outcome and decompose what did move. The delta evaluates as not-confirmed; this is not a failure of the team or the framework, it is the framework working. Write a follow-up delta that targets the gap.

**A hotfix needs to ship during the rollout.** Not a Release Delta. Operational work routes through the usual incident process. If the hotfix changes the targeting or reverses the rollout, that shows up in the flag platform's audit log and is captured in Outcome at evaluation.

**The flag platform changed names and my flag URL is wrong.** Update `links.flags`. Links are mutable on purpose. CI does not lock them.

**Multiple deltas share one flag.** Allowed. It usually means the work has been decomposed for measurement reasons, which is what the framework wants. Each delta has its own Hypothesis, Success Signal, and Outcome; the shared flag is an implementation detail.

**A delta's Horizon arrives but the data is not ready.** The framework treats Horizon as a commitment. If your data infrastructure routinely cannot deliver a six-week measurement in the seven weeks following a Horizon, that is a measurement-maturity issue worth surfacing. Mark the delta `evaluated` with an Outcome that says explicitly "data not yet available; will update," and update when the data lands. Do not let the delta sit in `active` past its Horizon.

## Getting help

For framework questions, see https://www.river-framework.dev. For repo conventions and CI failures, the error messages are written to be self-explanatory; if one is not, file an issue against this repo. For declaration review facilitation, contact {role/owner}.
