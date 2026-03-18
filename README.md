# Loss Aversion / Framing Task

![Maturity: smoke_tested](https://img.shields.io/badge/Maturity-smoke_tested-64748b?style=flat-square&labelColor=111827)

| Field | Value |
|---|---|
| Name | Loss Aversion / Framing Task |
| Version | v0.1.2-dev |
| URL / Repository | https://github.com/TaskBeacon/T000031-loss-aversion-framing |
| Short Description | Sure-vs-risk decision task with gain, loss, and mixed framing conditions. |
| Created By | TaskBeacon |
| Date Updated | 2026-03-18 |
| PsyFlow Version | 0.1.9 |
| PsychoPy Version | 2025.1.1 |
| Modality | Behavior |
| Language | Chinese |
| Voice Name | zh-CN-YunyangNeural (voice disabled by default) |

## 1. Task Overview

This task implements a risk-choice paradigm with three conditions:

- `gain_frame`: sure keep amount vs risky keep-all/keep-none option.
- `loss_frame`: sure loss amount vs risky full-loss/no-loss option.
- `mixed_frame`: sure amount vs mixed gain-loss lottery.

Each trial records choice, response latency, timeout status, and offer-level expected value metadata. Participant-facing text is Chinese and rendered with `SimHei`.

## 2. Task Flow

![Task Flow](task_flow.png)

### Block-Level Flow

| Step | Description |
|---|---|
| 1. Block init | `BlockUnit.generate_conditions(weights=settings.resolve_condition_weights())` resolves the per-block condition schedule. |
| 2. Trial execution | `run_trial(...)` realizes one framing trial per scheduled condition token. |
| 3. Block summary | Show block gamble rate, mean RT, and timeout count (except last block). |
| 4. Final summary | Show full-task gamble/RT metrics and condition-specific gamble rates. |

### Trial-Level Flow

| Step | Description |
|---|---|
| `fixation` | Present `+` for jittered fixation duration. |
| `decision` | Present framing label + scenario + safe/risky options; capture `f/j` response within deadline. |
| `feedback` | Show choice feedback or timeout feedback. |
| `iti` | Present jittered inter-trial fixation before next trial. |

### Controller Logic

| Component | Description |
|---|---|
| Offer sampling | Samples one offer from condition-specific banks declared in `task.offer_banks`. |
| Determinism | Uses `overall_seed` / `block_seed` plus trial identity for auditable replay. |
| Summary update | Computes block/session gamble rate, timeout rate, and mean RT from reduced trial rows. |

### Runtime Context Phases

| Phase Label | Meaning |
|---|---|
| `fixation` | Pre-decision baseline display. |
| `decision` | Active choice window with valid keys. |
| `feedback` | Post-choice or timeout acknowledgement. |
| `iti` | Inter-trial reset period. |

## 3. Configuration Summary

### a. Subject Info

| Field | Meaning |
|---|---|
| `subject_id` | 3-digit participant identifier. |

### b. Window Settings

| Parameter | Value |
|---|---|
| `size` | `[1280, 720]` |
| `units` | `pix` |
| `screen` | `0` |
| `bg_color` | `gray` |
| `fullscreen` | `false` |
| `monitor_width_cm` | `35.5` |
| `monitor_distance_cm` | `60` |

### c. Stimuli

| Stimulus Group | Description |
|---|---|
| `instruction_text` | Task instructions and key mapping. |
| `frame_label`, `scenario_text` | Condition label and scenario prompt. |
| `safe_option_text`, `gamble_option_text` | Left/right choice options shown simultaneously. |
| `key_hint` | On-screen reminder of safe/gamble key mapping. |
| `feedback_choice`, `feedback_timeout` | Response-dependent feedback text. |
| `fixation`, `block_break`, `good_bye` | Shared fixation and summary screens. |

### d. Timing

| Stage | Duration |
|---|---|
| fixation | jittered (`fixation_duration`) |
| decision | fixed deadline (`decision_deadline`) |
| feedback | fixed (`feedback_duration`) |
| iti | jittered (`iti_duration`) |

### e. Trigger Map

| Trigger | Code |
|---|---:|
| `exp_onset` | 1 |
| `exp_end` | 2 |
| `block_onset` | 10 |
| `block_end` | 11 |
| `fixation_onset` | 20 |
| `decision_onset` | 30 |
| `choice_safe` | 31 |
| `choice_gamble` | 32 |
| `choice_timeout` | 33 |
| `feedback_onset` | 40 |
| `iti_onset` | 50 |

### f. Offer Bank Parameters

| Parameter Group | Description |
|---|---|
| `task.conditions` | Block-level labels resolved by `BlockUnit.generate_conditions(...)`. |
| `task.offer_banks.gain_frame` | Sure keep vs probabilistic keep-all offers. |
| `task.offer_banks.loss_frame` | Sure loss vs probabilistic full-loss offers. |
| `task.offer_banks.mixed_frame` | Sure amount vs mixed gain/loss lotteries. |
| `enable_logging` | Emits per-trial offer sampling details to PsychoPy data log. |

## 4. Methods (for academic publication)

Participants performed a repeated risky-choice task under gain, loss, and mixed-outcome framing. On each trial they selected between a sure option and a gamble option using a two-key response mapping, under a bounded decision window. Trial-structured logs captured condition identity, offer parameters, expected-value fields, response choice, reaction time, and timeout events.

The implementation uses explicit phase instrumentation (`fixation`, `decision`, `feedback`, `iti`) with trigger-aligned event logging to support reproducible QA and downstream behavioral analysis of framing-dependent risk preference. Offer content is config-driven and sampled deterministically from `task.offer_banks`, so the task no longer depends on a separate task-local state manager.
