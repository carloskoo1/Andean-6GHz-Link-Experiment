# Incident 2026-09-15 — Failed 3x2 RF transition and recovery

## Status

Recovered.

The formal campaign executor remains intentionally stopped pending
hardening and validation of the recovery workflow.

## Context

Platform: AtmosLink / Andean 6 GHz Link Experiment

Link:

- CU01 / Cuñacales: AP, 192.168.1.8
- SJ01 / San José: SM, 192.168.1.9
- Raspberry Pi SJ01: 192.168.1.4
- Cambium Force 4600C, firmware 5.4.0
- Nominal pre-transition configuration: 7000 MHz / 20 MHz
- Scheduled first experimental treatment: F6655_B20
- Campaign start: 2026-09-15 00:00:00 America/Lima

## Incident summary

At the beginning of the formal 3x2 campaign, the orchestrator attempted
the scheduled transition from the existing 7000 MHz / 20 MHz
configuration to F6655_B20.

The AP accepted the trial configuration request. Connectivity was
observed immediately after the trial, but was subsequently lost toward
the remote side of the link.

The orchestrator did not obtain the required consecutive successful
connectivity probes and initiated rollback by cancelling the trial.

The expected connectivity was not restored during the rollback
verification window.

The campaign executor subsequently classified the transition as failed.
Because the original implementation persisted retry information but did
not persist a non-retryable recovery state, later executor invocations
could retry the same RF transition after the configured cooldown.

This behavior was identified as unsafe for unattended operation.

## Observed event sequence

Controller event timestamps are authoritative for this incident.

- 2026-09-15 00:00 local: SWITCH_START for F6655_B20.
- Trial configuration was accepted by the AP.
- First connectivity probe succeeded.
- Subsequent probes failed to establish the required stable sequence.
- SWITCH_FAILED was recorded because the link did not recover.
- ROLLBACK_START was initiated by cancellation of the trial.
- Rollback connectivity verification failed.
- ROLLBACK_FAILED was recorded.
- Later executor invocations were able to retry after the retry cooldown.

No valid F6655_B20 treatment was established.

## Failure signature observed during diagnosis

During the degraded state:

- CU01 AP 192.168.1.8 remained reachable locally by ICMP.
- The AP basic HTTPS service remained reachable.
- Authenticated management API test_connect became unresponsive and
  timed out.
- SJ01 SM 192.168.1.9 was unreachable from the Controller.
- Raspberry Pi SJ01 192.168.1.4 was unreachable from the Controller.
- The AP web interface displayed a persistent reboot-state message.

This combination is materially different from an isolated management
API timeout.

After recovery, an isolated/transient management API condition was also
observed while AP, SM and Raspberry Pi connectivity remained healthy.
Therefore an API timeout alone must not trigger power recovery.

## Recovery

The deployed cnMatrix EX1010-P remained operational in its forwarding
and PoE data plane even though its expected IPv4 management address was
not reachable.

Management access was recovered through the switch IPv6 link-local
interface.

The deployed switch was identified as the expected device and its PoE
port mapping was verified before any power action.

Relevant verified mapping:

- Port 3: Cunacales — 5.8 GHz AP — protected, not modified.
- Port 6: Cunacales6 — 6 GHz AP — recovery target.

A controlled PoE cycle was performed only on port 6.

During the power-off interval:

- 192.168.1.8 became unreachable as expected.
- 192.168.1.2, the 5.8 GHz AP on port 3, remained reachable.

This provided operational confirmation that the selected PoE port
corresponded to the 6 GHz AP.

After restoring PoE on port 6:

- CU01 AP 192.168.1.8 recovered.
- SJ01 SM 192.168.1.9 re-associated and recovered.
- Raspberry Pi SJ01 192.168.1.4 recovered.
- The authenticated Cambium API recovered.
- AP configuration was verified as 7000 MHz / 20 MHz.
- The SM remained running; it was not power-cycled.

## Root cause status

The exact internal cause has not been established.

Evidence supports a failure associated with the RF trial / transition
and subsequent AP management or configuration state, but the available
observations are insufficient to attribute the incident definitively to
firmware, RF scanning behavior, API implementation, or another internal
device mechanism.

No definitive root-cause statement should be made without additional
controlled evidence.

## Scientific-data disposition

The failed transition does not constitute a valid F6655_B20 treatment.

Measurements collected during the transition, failed rollback and
recovery interval must not be classified as stable F6655_B20
experimental observations.

The campaign schedule and resulting dataset must preserve the incident
rather than retrospectively treating the failed interval as a successful
experimental treatment.

A new formal treatment start must be established after the automation
and recovery mechanisms have been validated.

## Software hardening implemented

Following the incident, the campaign software was modified to introduce
a persistent SAFE_ABORT barrier.

If rollback itself fails, the orchestrator atomically creates:

    campaign_runtime/SAFE_ABORT.json

with status:

    RECOVERY_REQUIRED

and records that automatic RF transitions are blocked.

Two independent interlocks are implemented:

1. campaign_executor.py refuses to launch another RF transition while
   SAFE_ABORT exists.
2. campaign_orchestrator.py refuses a direct non-dry-run switch while
   SAFE_ABORT exists.

A blocked direct transition is recorded as:

    SWITCH_BLOCKED / SAFE_ABORT

rather than SWITCH_START, preserving event-log semantics.

Diagnostic operations such as validation, planning and preflight remain
available.

Dry-run operation remains available because it does not modify RF state.

## Verification

The hardening was validated using isolated temporary test directories
and simulated APIs. No live RF transition was required for these tests.

Regression status after hardening:

- Python compilation: PASS
- Unit tests: 25/25 PASS
- git diff --check: PASS
- Real campaign timer: inactive
- Real SAFE_ABORT file: absent

Tests include:

- rollback failure creates persistent RECOVERY_REQUIRED state;
- executor SAFE_ABORT prevents invocation of the transition runner;
- direct orchestrator switch is blocked by SAFE_ABORT;
- normal trial/confirm behavior remains functional;
- pre-confirmation and post-confirmation rollback paths remain covered.

## Recovery-manager requirements

Future automated recovery must not power-cycle the AP based on a single
failed ping or API timeout.

A recovery decision must use multiple independent signals, including
where applicable:

- AP ICMP reachability;
- AP HTTPS reachability;
- authenticated management API health;
- SM reachability/association;
- Raspberry Pi SJ01 reachability;
- active or failed RF transition context;
- persistent SAFE_ABORT state;
- expected cnMatrix identity;
- expected PoE port identity and description;
- current PoE delivery state.

The recovery implementation must:

- never reboot the entire cnMatrix switch;
- never modify protected port 3 during 6 GHz AP recovery;
- operate only on the verified 6 GHz AP PoE port;
- fail closed if switch or port identity cannot be established;
- record evidence before and after recovery;
- verify baseline RF configuration and end-to-end connectivity after
  recovery;
- keep recovery-period observations separate from valid treatment data.

Initial implementation should operate in diagnostic/supervised mode
before unattended PoE recovery is enabled.

## Additional observation: device clocks

During recovery, inconsistent device clocks were observed between the
Controller, AP and cnMatrix switch.

Controller timestamps should remain the authoritative event chronology
until device time synchronization is separately audited and corrected.
