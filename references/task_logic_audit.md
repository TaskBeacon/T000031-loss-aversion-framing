# Task Logic Audit: Loss Aversion / Framing Task

## 1. Paradigm Intent

- Task: `loss_aversion_framing`.
- Construct: risky-choice preference under gain/loss framing, including mixed gain-loss lotteries.
- Manipulated trial factor: condition family (`gain_frame`, `loss_frame`, `mixed_frame`) plus sampled offer parameters.
- Primary dependent measures:
  - gamble choice rate
  - condition-specific gamble rates
  - response time
  - timeout frequency.
- Key citations:
  - `W3024532045` (Ruggeri et al., 2020, Nature Human Behaviour)
  - `W4313429369` (Ert & Erev, 2013, Judgment and Decision Making)
  - `W2043214237` (Seymour et al., 2007, Journal of Neuroscience)

## 2. Block/Trial Workflow

### Block Structure

- Human profile: `3` blocks x `32` trials.
- QA/sim profiles: `1` block x `18` trials.
- Block setup:
  - `controller.start_block(block_idx)` resets block metrics.
  - `BlockUnit.generate_conditions()` samples configured condition tokens.

### Trial State Machine

1. `fixation`
- Stimulus: `fixation`.
- Trigger: `fixation_onset`.
- Keys: none.

2. `decision`
- Stimuli: `frame_label`, `scenario_text`, `safe_option_text`, `gamble_option_text`, `key_hint`.
- Trigger: `decision_onset`.
- Valid keys: `safe_key`, `gamble_key`.
- Response triggers: `choice_safe` / `choice_gamble`.
- Timeout trigger: `choice_timeout`.

3. `feedback`
- Trigger: `feedback_onset`.
- Stimulus branch:
  - `feedback_choice` for responded trials.
  - `feedback_timeout` for omitted trials.
- Keys: none.

4. `iti`
- Stimulus: `fixation`.
- Trigger: `iti_onset`.
- Keys: none.

## 3. Condition Semantics

- `gain_frame`:
  - sure keep amount vs risky keep-all/keep-none option.
  - emphasizes retained gains in wording.
- `loss_frame`:
  - sure loss amount vs risky full-loss/no-loss option.
  - emphasizes losses in wording.
- `mixed_frame`:
  - sure amount vs mixed gain/loss lottery.
  - includes both positive and negative gamble outcomes.

Each trial samples an offer from the condition-specific controller bank and logs `offer_id` plus EV-relevant parameters.

## 4. Response and Scoring Rules

- Key mapping (default):
  - `f -> safe` (`方案A`)
  - `j -> gamble` (`方案B`)
- Timeout policy:
  - no response key, `timed_out=true`
  - `chosen_option` empty
  - timeout feedback shown.
- Correctness logic: none (preference task).
- Metrics update:
  - `chose_gamble` recorded per responded trial
  - block and condition gamble-rate summaries computed in main runtime.
- QA-required output fields include:
  - `condition`, `block_id`, `trial_index`, `offer_id`, `response_key`, `chosen_option`, `timed_out`, `rt_s`.

## 5. Stimulus Layout Plan

- Decision screen (`1280x720`, `pix`):
  - `frame_label` at top center (`0, 255`) for condition salience.
  - `scenario_text` below frame label (`0, 170`).
  - `safe_option_text` left column (`-320, 20`, wrap `360`).
  - `gamble_option_text` right column (`320, 20`, wrap `360`).
  - `key_hint` near bottom (`0, -220`).
- Visual hierarchy:
  - frame/scenario context first, then side-by-side options, then key hint.
- Localization policy:
  - participant-facing labels/text are config-driven (`stimuli.*` and `task.choice_labels`), not hardcoded in `run_trial.py`.

## 6. Trigger Plan

| Trigger | Code | Semantics |
|---|---:|---|
| `exp_onset` | 1 | experiment start |
| `exp_end` | 2 | experiment end |
| `block_onset` | 10 | block start |
| `block_end` | 11 | block end |
| `fixation_onset` | 20 | fixation onset |
| `decision_onset` | 30 | decision display onset |
| `choice_safe` | 31 | safe option chosen |
| `choice_gamble` | 32 | gamble option chosen |
| `choice_timeout` | 33 | no response before deadline |
| `feedback_onset` | 40 | feedback onset |
| `iti_onset` | 50 | inter-trial interval onset |

## 7. Architecture Decisions (Auditability)

- `main.py` keeps one mode-aware flow (`human|qa|sim`) with identical trial orchestration and summary computation.
- `src/run_trial.py` removes MID-template states and uses framing-native phases (`fixation -> decision -> feedback -> iti`).
- Safe/gamble response triggers are emitted after mapping response key to semantic choice.
- Decision trial context includes `safe_key` and `gamble_key`, enabling sampler responders to act from explicit mappings.
- Offer semantics are sampled by controller and logged (`offer_id`, EV fields) for reproducible audit traces.

## 8. Inference Log

- Offer-bank magnitudes/probabilities are implementation inferences constrained by framing literature semantics, not one universal citation-prescribed item list.
- Human run uses three blocks for stable condition-wise rate estimates; QA/sim downsample trial counts for operational validation speed.
- Feedback wording for chosen option is template-driven in config (`task.feedback_choice_template`) as a localization portability inference.
- No monetary accumulation is tracked online; this is an inference to keep the task focused on framing-dependent choice preference rather than running wealth dynamics.
