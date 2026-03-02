# Stimulus Mapping

Task: `Loss Aversion / Framing Task`

| Condition | Implemented Stimulus IDs | Source Paper ID | Evidence (quote/figure/table) | Implementation Mode | Notes |
|---|---|---|---|---|---|
| `gain_frame` | `frame_label`, `scenario_text`, `safe_option_text`, `gamble_option_text`, `key_hint`, `feedback_choice`, `feedback_timeout`, `fixation` | `W3024532045` | Risk decisions under gain framing are implemented as sure-vs-gamble options with explicit probabilities/outcomes. | `psychopy_builtin` | Left/right option layout is fixed; content values are trial-formatted from controller offer banks. |
| `loss_frame` | `frame_label`, `scenario_text`, `safe_option_text`, `gamble_option_text`, `key_hint`, `feedback_choice`, `feedback_timeout`, `fixation` | `W3024532045` | Loss framing is implemented as sure loss versus probabilistic larger loss/no-loss alternatives. | `psychopy_builtin` | Condition-specific text is generated per trial using sampled loss offers. |
| `mixed_frame` | `frame_label`, `scenario_text`, `safe_option_text`, `gamble_option_text`, `key_hint`, `feedback_choice`, `feedback_timeout`, `fixation` | `W4313429369` | Mixed gain/loss lotteries are implemented against a sure baseline option to capture loss-aversion tendency. | `psychopy_builtin` | Mixed trials include both positive and negative outcomes in one gamble option. |
| `all_conditions` | `instruction_text`, `block_break`, `good_bye` | `W2140619986` | Shared instructions and summary screens provide a stable decision-task envelope across conditions. | `psychopy_builtin` | Participant-facing Chinese text and SimHei font are consistent across modes. |

Implementation mode legend:
- `psychopy_builtin`: stimulus rendered via PsychoPy primitives in config.
- `generated_reference_asset`: task-specific synthetic assets generated from reference-described stimulus rules.
- `licensed_external_asset`: externally sourced licensed media with protocol linkage.
