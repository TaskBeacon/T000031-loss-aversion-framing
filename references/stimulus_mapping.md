# Stimulus Mapping

Task: `Loss Aversion / Framing Task`

| Condition | Implemented Stimulus IDs | Source Paper ID | Evidence (quote/figure/table) | Implementation Mode | Notes |
|---|---|---|---|---|---|
| `gain_frame` | `gain_frame_cue`, `gain_frame_target` | `W2985923507` | Methods section describes condition-specific cue-target structure and response phase. | `psychopy_builtin` | Cue label text for GAIN FRAME; target token for condition-specific response context. |
| `loss_frame` | `loss_frame_cue`, `loss_frame_target` | `W2985923507` | Methods section describes condition-specific cue-target structure and response phase. | `psychopy_builtin` | Cue label text for LOSS FRAME; target token for condition-specific response context. |
| `mixed_frame` | `mixed_frame_cue`, `mixed_frame_target` | `W2985923507` | Methods section describes condition-specific cue-target structure and response phase. | `psychopy_builtin` | Cue label text for MIXED FRAME; target token for condition-specific response context. |

Implementation mode legend:
- `psychopy_builtin`: stimulus rendered via PsychoPy primitives in config.
- `generated_reference_asset`: task-specific synthetic assets generated from reference-described stimulus rules.
- `licensed_external_asset`: externally sourced licensed media with protocol linkage.
