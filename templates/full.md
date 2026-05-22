---
id: RD-NNNN
title: {short title naming the release}
status: proposed
type: growth
declared: YYYY-MM-DD
evaluated:
owners:
  product: {name or handle}
  engineering: {name or handle}
  operations: {name or handle}
links:
  flags:
    - {flag URL on your platform of record}
  experiments: []
  dashboards:
    - {dashboard URL for the metric being moved}
related:
  supersedes: []
  superseded_by: []
  depends_on: []
---

<!--
Sections below (Hypothesis, Success Signal, Target Cohort, Horizon)
are immutable once status is past `proposed`. Edits to a declared
delta should be made by superseding, not by rewriting.
-->

# {Short title naming the release}

## Context
{Why now. What prompted this release. Two or three sentences. Optional but useful for future readers and for evaluators who are not the original authors.}

## Hypothesis
{What we believe will happen when the target cohort encounters this.}

## Success Signal
- Metric: {the metric being moved}
- Direction: {up | down}
- Magnitude: {threshold the metric must cross}
- Window: {duration over which the signal must hold}

## Target Cohort
{Who this is for. How exposure will progress through the cohort, with the criterion that gates each stage.}

## Horizon
{The date by which we expect to know.}

## Guardrails
{Metrics that, if degraded, will pause or reverse the rollout. Each guardrail names the metric, the threshold, and the action triggered.}

## Reversibility
{How this release can be pulled back. Which flag, which targeting rule, expected time to full reversal. If a database migration or other forward-only change is involved, name it explicitly.}

## Out of scope
{What this delta is not claiming. Useful when a release touches several user journeys but only one is being measured.}

## Notes
{Discussion captured during declaration review. Free-form. Not part of the commitment.}

## Outcome
{Filled in at evaluation. Hypothesis held or did not. What the success signal did. What was learned. Any follow-up Release Deltas this generates.}
