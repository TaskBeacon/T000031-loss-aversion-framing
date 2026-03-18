# Task Plot Audit

- generated_at: 2026-03-18T23:53:32
- mode: existing
- task_path: E:\xhmhc\TaskBeacon\T000031-loss-aversion-framing

## 1. Inputs and provenance

- E:\xhmhc\TaskBeacon\T000031-loss-aversion-framing\README.md
- E:\xhmhc\TaskBeacon\T000031-loss-aversion-framing\config\config.yaml
- E:\xhmhc\TaskBeacon\T000031-loss-aversion-framing\src\run_trial.py

## 2. Evidence extracted from README

- | Step | Description |
- |---|---|
- | `fixation` | Present `+` for jittered fixation duration. |
- | `decision` | Present framing label + scenario + safe/risky options; capture `f/j` response within deadline. |
- | `feedback` | Show choice feedback or timeout feedback. |
- | `iti` | Present jittered inter-trial fixation before next trial. |

## 3. Evidence extracted from config/source

- gain_frame: phase=fixation, deadline_expr=fixation_duration, response_expr=n/a, stim_expr='fixation'
- gain_frame: phase=decision, deadline_expr=decision_deadline, response_expr=n/a, stim_expr='frame_label+scenario_text+safe_option_text+gamble_option_text+key_hint'
- gain_frame: phase=feedback, deadline_expr=feedback_duration, response_expr=n/a, stim_expr='feedback_timeout' if timed_out else 'feedback_choice'
- gain_frame: phase=iti, deadline_expr=iti_duration, response_expr=n/a, stim_expr='fixation'
- loss_frame: phase=fixation, deadline_expr=fixation_duration, response_expr=n/a, stim_expr='fixation'
- loss_frame: phase=decision, deadline_expr=decision_deadline, response_expr=n/a, stim_expr='frame_label+scenario_text+safe_option_text+gamble_option_text+key_hint'
- loss_frame: phase=feedback, deadline_expr=feedback_duration, response_expr=n/a, stim_expr='feedback_timeout' if timed_out else 'feedback_choice'
- loss_frame: phase=iti, deadline_expr=iti_duration, response_expr=n/a, stim_expr='fixation'
- mixed_frame: phase=fixation, deadline_expr=fixation_duration, response_expr=n/a, stim_expr='fixation'
- mixed_frame: phase=decision, deadline_expr=decision_deadline, response_expr=n/a, stim_expr='frame_label+scenario_text+safe_option_text+gamble_option_text+key_hint'
- mixed_frame: phase=feedback, deadline_expr=feedback_duration, response_expr=n/a, stim_expr='feedback_timeout' if timed_out else 'feedback_choice'
- mixed_frame: phase=iti, deadline_expr=iti_duration, response_expr=n/a, stim_expr='fixation'

## 4. Mapping to task_plot_spec

- timeline collection: one representative timeline per unique trial logic
- phase flow inferred from run_trial set_trial_context order and branch predicates
- participant-visible show() phases without set_trial_context are inferred where possible and warned
- duration/response inferred from deadline/capture expressions
- stimulus examples inferred from stim_id + config stimuli
- conditions with equivalent phase/timing logic collapsed and annotated as variants
- root_key: task_plot_spec
- spec_version: 0.2

## 5. Style decision and rationale

- Single timeline-collection view selected by policy: one representative condition per unique timeline logic.

## 6. Rendering parameters and constraints

- output_file: task_flow.png
- dpi: 300
- max_conditions: 3
- screens_per_timeline: 6
- screen_overlap_ratio: 0.1
- screen_slope: 0.08
- screen_slope_deg: 25.0
- screen_aspect_ratio: 1.4545454545454546
- qa_mode: local
- auto_layout_feedback:
  - layout pass 1: crop-only; left=0.054, right=0.055, blank=0.163
- auto_layout_feedback_records:
  - pass: 1
    metrics: {'left_ratio': 0.0544, 'right_ratio': 0.0552, 'blank_ratio': 0.163}

## 7. Output files and checksums

- E:\xhmhc\TaskBeacon\T000031-loss-aversion-framing\references\task_plot_spec.yaml: sha256=55209f5123369e6d4494afc590d4afa95b2733486a25e6739f414c4f2a5b69a6
- E:\xhmhc\TaskBeacon\T000031-loss-aversion-framing\references\task_plot_spec.json: sha256=66009cc07e560ec16a65410bf9bb6b5ccc1380f7cb4c8c66596be5a4f1f35b89
- E:\xhmhc\TaskBeacon\T000031-loss-aversion-framing\references\task_plot_source_excerpt.md: sha256=ea5ab3c76609848215385ba3e7fff0442cc34dd9676511749a4faa5806466623
- E:\xhmhc\TaskBeacon\T000031-loss-aversion-framing\task_flow.png: sha256=210a580bed94149291d91f087e5a5e0aca3cb348c805541fa5f3739ac8d61af7

## 8. Inferred/uncertain items

- gain_frame:fixation:heuristic numeric parse from 'getattr(settings, 'fixation_duration', 0.5)'
- gain_frame:decision:heuristic numeric parse from 'getattr(settings, 'decision_deadline', 4.0)'
- gain_frame:feedback:heuristic numeric parse from 'getattr(settings, 'feedback_duration', 0.7)'
- gain_frame:iti:heuristic numeric parse from 'getattr(settings, 'iti_duration', 0.5)'
- loss_frame:fixation:heuristic numeric parse from 'getattr(settings, 'fixation_duration', 0.5)'
- loss_frame:decision:heuristic numeric parse from 'getattr(settings, 'decision_deadline', 4.0)'
- loss_frame:feedback:heuristic numeric parse from 'getattr(settings, 'feedback_duration', 0.7)'
- loss_frame:iti:heuristic numeric parse from 'getattr(settings, 'iti_duration', 0.5)'
- mixed_frame:fixation:heuristic numeric parse from 'getattr(settings, 'fixation_duration', 0.5)'
- mixed_frame:decision:heuristic numeric parse from 'getattr(settings, 'decision_deadline', 4.0)'
- mixed_frame:feedback:heuristic numeric parse from 'getattr(settings, 'feedback_duration', 0.7)'
- mixed_frame:iti:heuristic numeric parse from 'getattr(settings, 'iti_duration', 0.5)'
- unparsed if-tests defaulted to condition-agnostic applicability: response_key == safe_key; timed_out
