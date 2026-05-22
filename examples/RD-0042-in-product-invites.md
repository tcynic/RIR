---
id: RD-0042
title: Add in-product workspace invite flow
status: evaluated
type: growth
declared: 2026-04-26
evaluated: 2026-08-15
owners:
  product: jane.chen@example.com
  engineering: alex.park@example.com
  operations: sam.morales@example.com
links:
  flags:
    - https://app.launchdarkly.com/projects/default/flags/growth-in-product-invites
  experiments:
    - https://console.statsig.com/experiments/in_product_invites_v1
  dashboards:
    - https://looker.example.com/dashboards/workspace-expansion
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

# Add in-product workspace invite flow

## Context
Workspace expansion currently happens through admin-driven email invites sent from the settings page. Invitee activation runs at roughly 35% on a four-week window. Internal analysis shows that workspaces growing past five members in their first thirty days retain at three times the rate of workspaces that do not. Lowering the friction of inviting, by surfacing contextual prompts when an admin shares an asset, is hypothesized to drive both invite volume and downstream new-user activation.

## Hypothesis
Workspace admins exposed to contextual in-product invite prompts will produce more newly activated users per workspace than admins relying on the settings-page invite flow alone.

## Success Signal
- Metric: New activated users per workspace, within the exposed cohort, attributed to invites sent during the measurement window.
- Direction: up.
- Magnitude: at least 20% lift versus the control cohort.
- Window: six weeks of measurement after the rollout reaches 100% of the target cohort.

## Target Cohort
Workspace admins on Pro and Business plans, in workspaces with two to ten active members, English-language UI. Single-user workspaces are excluded because they have no one to invite. Workspaces with eleven or more active members are excluded because invitation patterns in those workspaces are already established and the marginal effect of contextual prompts is expected to be small.

Progressive exposure proceeds in four stages: 5% (one week), 25% (one week), 50% (two weeks), 100%. Each stage is gated on the guardrails below passing for the duration of the prior stage.

## Horizon
Decision by 2026-08-15. Sixteen weeks from declaration covers four weeks of cohort progression to full rollout, six weeks of measurement at 100%, and a buffer for evaluation and writeup.

## Guardrails
- Email spam complaint rate in the exposed cohort exceeds 0.1% over any seven-day window: pause rollout.
- Workspace abandonment rate (workspaces with no admin activity in the seven days following an invite send) rises more than 5% versus the control cohort: pause rollout.
- Invitee activation rate within the exposed cohort drops below 25%, against a baseline of 35%: reverse the release.

## Reversibility
Single flag `growth-in-product-invites` controls the feature. Reversal is flag-off, expected effective time under two minutes, no redeploy required. No database migration is involved; invite records produced before reversal continue to function. Email sends already in the queue at reversal will complete normally.

## Out of scope
Invite acceptance UX (a separate workstream owned by the onboarding team). Bulk invite functionality (deferred, candidate for a follow-on delta). Changes to the invite email template (deferred).

## Notes
Declaration review held 2026-04-22. Operations raised concern about email volume; engineering committed to rate-limiting at five invites per admin per day, well above the current baseline of approximately 1.2 invites per active admin per week. Product flagged the eleven-or-more-member exclusion for revisit if results in qualifying cohorts are positive.

## Outcome
The hypothesis did not hold at the declared magnitude. New activated users per workspace lifted 18% versus control over the six-week measurement window, against a 20% threshold. The release is not called confirmed, and the release is not called reversed.

Decomposition: invites sent per active admin rose 41% versus control, well above expectations. Invitee activation in the exposed cohort fell from a baseline of 35% to 32%, partially offsetting the volume gain. The net effect on new activated users per workspace was positive but below threshold.

What we learned: contextual in-product prompts drive meaningful invite volume, and the marginal invitee acquired through this surface activates at a lower rate than the marginal invitee from the settings page. The most plausible explanation is that contextual prompts encourage admins to invite collaborators on specific assets, who skew toward weaker workspace fit than the core team members an admin invites from a settings page.

The feature stays on at 100%. Volume gains are real, the activation gap is small, and reversal is not warranted. Two follow-up deltas will pursue the structural finding: RD-0058 will test invitee onboarding improvements targeted at the contextual-invite source, and RD-0061 will explore restricting in-product prompts to asset types where contextual relevance is highest, on the theory that targeting tightens the activation gap.

Guardrails: no guardrail triggered during the rollout. Spam complaint rate held at 0.04%, abandonment rate moved within 1% of control, invitee activation never approached the 25% reversal floor.
