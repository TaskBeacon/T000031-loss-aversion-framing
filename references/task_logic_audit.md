# Task Logic Audit: Loss Aversion / Framing Task

## 1. Paradigm Intent

- Task: `loss_aversion_framing`
- Primary construct: risk preference modulation by gain/loss framing, plus mixed-gamble loss aversion tendency.
- Manipulated factors: trial condition (`gain_frame`, `loss_frame`, `mixed_frame`) and offer parameters sampled from condition-specific offer pools.
- Dependent measures: choice (`safe` vs `gamble`), response latency, timeout rate, condition-level gamble rate.
- Key citations:
  - `W3024532045` (Ruggeri et al., 2020, *Nature Human Behaviour*)
  - `W4313429369` (Ert & Erev, 2013, *Judgment and Decision Making*)
  - `W2043214237` (Seymour et al., 2007, *Journal of Neuroscience*)

## 2. Block/Trial Workflow

### Block Structure

- Total blocks: `3`
- Trials per block: `32`
- Randomization/counterbalancing: `BlockUnit.generate_conditions()` draws configured conditions; per trial, the controller samples a concrete offer from that condition's offer bank.

### Trial State Machine

1. `fixation`
   - Onset trigger: `fixation_onset`
   - Stimuli shown: central fixation cross (`fixation`).
   - Valid keys: `[]`
   - Timeout behavior: auto-advance after sampled fixation duration.
   - Next state: `decision`

2. `decision`
   - Onset trigger: `decision_onset`
   - Stimuli shown together:
     - `frame_label` (condition label)
     - `scenario_text` (trial budget/scenario text)
     - `safe_option_text` (sure option)
     - `gamble_option_text` (risky option)
     - `key_hint` (A/B key reminder)
   - Valid keys: `[safe_key, gamble_key]` (`f/j` by default)
   - Timeout behavior: if no response before deadline, emit `choice_timeout` and mark trial as timeout.
   - Response triggers:
     - safe response: `choice_safe`
     - gamble response: `choice_gamble`
   - Next state: `feedback`

3. `feedback`
   - Onset trigger: `feedback_onset`
   - Stimuli shown:
     - `feedback_choice` when participant responded, or
     - `feedback_timeout` when no response.
   - Valid keys: `[]`
   - Timeout behavior: auto-advance after fixed feedback duration.
   - Next state: `iti`

4. `iti`
   - Onset trigger: `iti_onset`
   - Stimuli shown: fixation cross (`fixation`).
   - Valid keys: `[]`
   - Timeout behavior: auto-advance after sampled ITI duration.
   - Next state: next trial.

## 3. Condition Semantics

- Condition ID: `gain_frame`
  - Participant-facing meaning: gain-framed choice between a sure keep amount vs probabilistic keep-all/keep-none option.
  - Concrete stimulus realization:
    - frame label: `收益框架`
    - scenario: `你获得 X 元预算。请选择其一：`
    - safe option: `方案A（确定） 保留 ...`
    - gamble option: `方案B（风险） p% 保留 ... / (1-p)% 保留 0`
  - Outcome fields: `chosen_option`, `chose_gamble`, `rt_s`, `timed_out`, EV metadata.

- Condition ID: `loss_frame`
  - Participant-facing meaning: loss-framed choice between a sure loss vs probabilistic full-loss/no-loss option.
  - Concrete stimulus realization:
    - frame label: `损失框架`
    - scenario: `你获得 X 元预算。请选择其一：`
    - safe option: `方案A（确定） 损失 ...`
    - gamble option: `方案B（风险） p% 损失 0 / (1-p)% 损失 ...`
  - Outcome fields: same schema as gain condition.

- Condition ID: `mixed_frame`
  - Participant-facing meaning: mixed gamble choice comparing sure amount (often 0) to gain/loss lottery.
  - Concrete stimulus realization:
    - frame label: `混合框架`
    - scenario: `请选择其一：`
    - safe option: `方案A（确定） 获得/损失 ...`
    - gamble option: `方案B（风险） p% 获得 ... / (1-p)% 损失 ...`
  - Outcome fields: same schema as gain/loss conditions.

## 4. Response and Scoring Rules

- Response mapping: `safe_key=f`, `gamble_key=j` (configurable).
- Missing-response policy: timeout trials are explicitly logged with `timed_out=true`, no choice assignment, and timeout feedback text.
- Correctness logic: none (preference task, not right/wrong discrimination).
- Reward/penalty updates: no online points economy; controller updates behavioral metrics only.
- Running metrics:
  - block/session: gamble rate, timeout rate, mean RT.
  - condition-level: block gamble rate and trial count.

## 5. Stimulus Layout Plan

- Decision screen spatial layout (all text stimuli are rendered concurrently):
  - `frame_label`: top center `pos [0, 255]`, height `34`, yellow-tinted for condition salience.
  - `scenario_text`: upper center `pos [0, 170]`, height `30`.
  - `safe_option_text`: left option column `pos [-320, 20]`, wrap `360`.
  - `gamble_option_text`: right option column `pos [320, 20]`, wrap `360`.
  - `key_hint`: bottom center `pos [0, -220]`, height `24`.
- Visual hierarchy: condition/scenario first, then two options in left-right parallel layout, then response hint.
- Readability constraints: all participant-facing Chinese text uses `font: SimHei`; wrap widths are set to prevent overlap on `1280x720`.

## 6. Trigger Plan

| Trigger | Code | Semantics |
|---|---:|---|
| `exp_onset` | 1 | experiment start |
| `exp_end` | 2 | experiment end |
| `block_onset` | 10 | block start |
| `block_end` | 11 | block end |
| `fixation_onset` | 20 | fixation phase onset |
| `decision_onset` | 30 | decision screen onset |
| `choice_safe` | 31 | safe option key response |
| `choice_gamble` | 32 | gamble option key response |
| `choice_timeout` | 33 | no response before deadline |
| `feedback_onset` | 40 | feedback phase onset |
| `iti_onset` | 50 | inter-trial interval onset |

## 7. Inference Log

- Decision: use three condition families (`gain_frame`, `loss_frame`, `mixed_frame`) in one task implementation.
- Why inference was required: source literature varies in whether framing and mixed-gamble manipulations are presented in separate experiments.
- Citation-supported rationale: all selected papers address risk decisions under gain/loss framing or mixed gain-loss valuation; merged implementation preserves these core manipulations in an auditable single protocol.

- Decision: default offer magnitudes/probabilities are configured as reusable offer banks instead of one fixed canonical schedule.
- Why inference was required: selected papers report paradigm logic and choice patterns, but not one universal item list for all contexts.
- Citation-supported rationale: configurable offer banks preserve sure-vs-risk framing structure while enabling reproducible tuning via config.
