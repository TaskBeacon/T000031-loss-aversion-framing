# CHANGELOG

## [v0.1.3-dev] - 2026-03-02

### Changed
- Replaced `src/run_trial.py` MID-template stages with framing-native trial flow (`fixation -> decision -> feedback -> iti`).
- Added config-first localization helpers in task config (`task.choice_labels`, `task.feedback_choice_template`) and used them for feedback wording.
- Rebuilt all reference artifacts to the current contract schema (`references.yaml`, `references.md`, `parameter_mapping.md`, `stimulus_mapping.md`, `task_logic_audit.md`).

### Fixed
- Restored QA-required trial columns in runtime output (`trial_index`, `offer_id`, `response_key`, `chosen_option`, `timed_out`, `rt_s`).
- Removed remaining MID cue/anticipation/target dependencies from runtime implementation.
- Restored contract-required reference headings and table columns, including task logic sections `## 7` and `## 8`.

## [v0.1.2-dev] - 2026-02-19

### Changed
- Repaired paradigm implementation from MID-derived cue/target flow to framing-specific `fixation -> decision -> feedback -> iti` trial logic.
- Replaced MID adaptive controller with offer-sampling controller for `gain_frame`, `loss_frame`, and `mixed_frame` conditions.
- Updated all configs to Chinese participant-facing stimuli (`SimHei`) with explicit left/right option layout and framing-specific trigger map.
- Reworked sampler responder to act on `decision` phase and safe/gamble key semantics.
- Rebuilt references bundle (`task_logic_audit.md`, `stimulus_mapping.md`, `parameter_mapping.md`, `references.*`, `selected_papers.json`) to literature-first framing evidence.
- Synced metadata docs (`README.md`, `taskbeacon.yaml`) with repaired runtime behavior.

### Fixed
- Removed legacy MID paradigm descriptions from task documentation and evidence artifacts.

### Verified
- `python -m py_compile src/run_trial.py src/utils.py main.py responders/task_sampler.py`
- `python E:/Taskbeacon/psyflow/skills/task-build/scripts/check_task_standard.py --task-path E:/Taskbeacon/T000031-loss-aversion-framing`
- `python -m psyflow.validate E:/Taskbeacon/T000031-loss-aversion-framing`
- `psyflow-qa E:/Taskbeacon/T000031-loss-aversion-framing --config config/config_qa.yaml --no-maturity-update`
- `python main.py sim --config config/config_scripted_sim.yaml`
- `python main.py sim --config config/config_sampler_sim.yaml`

## [v0.1.1-dev] - 2026-02-19

### Changed
- Rebuilt literature bundle with task-relevant curated papers and regenerated reference artifacts.
- Replaced corrupted `references/task_logic_audit.md` with a full state-machine audit.
- Updated `references/stimulus_mapping.md` to concrete implemented stimulus IDs per condition.
- Synced metadata (`README.md`, `taskbeacon.yaml`) with current configuration and evidence.

All notable development changes for `T000031-loss-aversion-framing` are documented here.

## [0.1.0] - 2026-02-17

### Added
- Added initial PsyFlow/TAPS task scaffold for Loss Aversion / Framing Task.
- Added mode-aware runtime (`human|qa|sim`) in `main.py`.
- Added split configs (`config.yaml`, `config_qa.yaml`, `config_scripted_sim.yaml`, `config_sampler_sim.yaml`).
- Added responder trial-context plumbing via `set_trial_context(...)` in `src/run_trial.py`.
- Added generated cue/target image stimuli under `assets/generated/`.

### Verified
- `python -m psyflow.validate <task_path>`
- `psyflow-qa <task_path> --config config/config_qa.yaml --no-maturity-update`
- `python main.py sim --config config/config_scripted_sim.yaml`
- `python main.py sim --config config/config_sampler_sim.yaml`

