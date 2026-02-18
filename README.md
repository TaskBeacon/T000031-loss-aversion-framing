# Loss Aversion / Framing Task

![Maturity: draft](https://img.shields.io/badge/Maturity-draft-64748b?style=flat-square&labelColor=111827)

| Field | Value |
|---|---|
| Name | Loss Aversion / Framing Task |
| Version | v0.1.1-dev |
| URL / Repository | https://github.com/TaskBeacon/T000031-loss-aversion-framing |
| Short Description | Prospect-theory style framing and loss-aversion choices. |
| Created By | TaskBeacon |
| Date Updated | 2026-02-19 |
| PsyFlow Version | 0.1.9 |
| PsychoPy Version | 2025.1.1 |
| Modality | Behavior |
| Language | Chinese |
| Voice Name | zh-CN-YunyangNeural (voice disabled by default) |

## 1. Task Overview

This task implements a framing-based choice paradigm with `gain_frame`, `loss_frame`, and `mixed_frame` conditions. Each trial includes cue, anticipation, target response capture, and outcome feedback.

The implementation is organized for standardized execution and logging across human, QA, scripted sim, and sampler sim modes.

## 2. Task Flow

### Block-Level Flow

| Step | Description |
|---|---|
| 1. Prepare schedule | Frame condition schedule is loaded for each block. |
| 2. Execute trials | `run_trial(...)` runs cue, anticipation, target, and feedback stages. |
| 3. Block summary | Accuracy and cumulative score are shown. |
| 4. End summary | Final total score is shown at task completion. |

### Trial-Level Flow

| Step | Description |
|---|---|
| Cue | Frame-specific cue is shown. |
| Anticipation | Fixation stage before target response window. |
| Target | Condition target appears and response is captured. |
| Pre-feedback fixation | Brief fixation transition stage. |
| Feedback | Hit/miss feedback and score delta are shown. |

### Controller Logic

| Component | Description |
|---|---|
| Adaptive timing | Controller tunes target duration around target accuracy. |
| Condition tracking | Performance history is tracked per frame condition. |
| Score update | Trial outcome updates running score. |

### Runtime Context Phases

| Phase Label | Meaning |
|---|---|
| `anticipation` | Pre-target response-monitoring interval. |
| `target` | Main target-response interval. |

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

| Name | Type | Description |
|---|---|---|
| `*_cue` | text | Frame-specific cue prompts. |
| `*_target` | text | Frame condition targets used for response capture. |
| `*_hit_feedback`, `*_miss_feedback` | text | Condition-specific feedback displays. |
| `fixation`, `block_break`, `good_bye` | text | Shared fixation and summary displays. |

### d. Timing

| Phase | Duration |
|---|---|
| cue | 0.5 s |
| anticipation | 1.0 s |
| prefeedback | 0.4 s |
| feedback | 0.8 s |
| target | adaptive via controller (`0.08`-`0.40` s bounds) |

## 4. Methods (for academic publication)

Participants completed framed choice trials designed to probe valuation asymmetries across gain, loss, and mixed contexts. Each trial included frame cueing, response-window target presentation, and immediate trial feedback.

A controller maintained bounded adaptive timing based on recent response outcomes. Trial-level data capture included condition identity, response success, response timing, and score updates.

Trigger emissions were defined for all major trial stages to support synchronized recording and reproducible QA validation.
