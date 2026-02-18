# Stimulus Mapping

Task: `Loss Aversion / Framing Task`

| Condition | Implemented Stimulus IDs | Source Paper ID | Evidence (quote/figure/table) | Implementation Mode | Notes |
|---|---|---|---|---|---|
| `gain_frame` | `gain_frame_cue`, `gain_frame_target`, `gain_frame_hit_feedback`, `gain_frame_miss_feedback`, `fixation` | `W1989005086` | Condition-specific trial flow and outcome/response mapping described in selected paradigm references. | `psychopy_builtin` | Condition row resolved against current `config/config.yaml` stimuli and `src/run_trial.py` phase logic. |
| `loss_frame` | `loss_frame_cue`, `loss_frame_target`, `loss_frame_hit_feedback`, `loss_frame_miss_feedback`, `fixation` | `W1989005086` | Condition-specific trial flow and outcome/response mapping described in selected paradigm references. | `psychopy_builtin` | Condition row resolved against current `config/config.yaml` stimuli and `src/run_trial.py` phase logic. |
| `mixed_frame` | `mixed_frame_cue`, `mixed_frame_target`, `mixed_frame_hit_feedback`, `mixed_frame_miss_feedback`, `fixation` | `W1989005086` | Condition-specific trial flow and outcome/response mapping described in selected paradigm references. | `psychopy_builtin` | Condition row resolved against current `config/config.yaml` stimuli and `src/run_trial.py` phase logic. |
| `all_conditions` | `instruction_text`, `block_break`, `good_bye`, `fixation` | `W1989005086` | Shared instruction, transition, and fixation assets support the common task envelope across all conditions. | `psychopy_builtin` | Shared assets are condition-agnostic and used in every run mode. |

Implementation mode legend:
- `psychopy_builtin`: stimulus rendered via PsychoPy primitives in config.
- `generated_reference_asset`: task-specific synthetic assets generated from reference-described stimulus rules.
- `licensed_external_asset`: externally sourced licensed media with protocol linkage.
