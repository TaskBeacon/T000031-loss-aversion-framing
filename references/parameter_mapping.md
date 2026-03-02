# Parameter Mapping

| Parameter | Implemented Value | Source Paper ID | Confidence | Rationale |
|---|---|---|---|---|
| `task.conditions` | `['gain_frame', 'loss_frame', 'mixed_frame']` | `W3024532045` | `high` | Implements gain/loss framing plus mixed-risk choices in one schedule. |
| `task.total_blocks` | `3` | `W3024532045` | `inferred` | Multi-block design improves within-subject sampling across condition families. |
| `task.trial_per_block` | `32` | `W3024532045` | `inferred` | Fixed block length supports stable per-condition estimate aggregation. |
| `task.safe_key` | `f` | `W2140619986` | `inferred` | Two-key mapping for forced-choice decision capture. |
| `task.gamble_key` | `j` | `W2140619986` | `inferred` | Two-key mapping for forced-choice decision capture. |
| `timing.fixation_duration` | `[0.4, 0.7]` | `W2013390773` | `inferred` | Short jittered pre-decision fixation reduces rhythmic expectancy. |
| `timing.decision_deadline` | `4.0` | `W2013390773` | `inferred` | Bounded response window for decision latency capture and timeout handling. |
| `timing.feedback_duration` | `0.7` | `W2013390773` | `inferred` | Brief post-choice acknowledgement before ITI. |
| `timing.iti_duration` | `[0.4, 0.8]` | `W2013390773` | `inferred` | Jittered ITI separates consecutive decisions. |
| `controller.gain_trials` | `sure keep vs probabilistic keep-all list` | `W3024532045` | `inferred` | Gain-frame offers preserve sure-vs-risk structure with explicit probabilities. |
| `controller.loss_trials` | `sure loss vs probabilistic full-loss list` | `W3024532045` | `inferred` | Loss-frame offers preserve sure-loss vs gamble-loss structure. |
| `controller.mixed_trials` | `sure amount vs gain/loss lottery list` | `W4313429369` | `inferred` | Mixed lotteries capture loss-aversion-sensitive valuation behavior. |
| `triggers.map.fixation_onset` | `20` | `W2043214237` | `inferred` | Marks pre-decision baseline period. |
| `triggers.map.decision_onset` | `30` | `W2043214237` | `inferred` | Marks decision option display onset. |
| `triggers.map.choice_safe` | `31` | `W2043214237` | `inferred` | Encodes safe-option response event. |
| `triggers.map.choice_gamble` | `32` | `W2043214237` | `inferred` | Encodes gamble-option response event. |
| `triggers.map.choice_timeout` | `33` | `W2043214237` | `inferred` | Encodes missed response event. |
| `triggers.map.feedback_onset` | `40` | `W2043214237` | `inferred` | Marks feedback presentation onset. |
| `triggers.map.iti_onset` | `50` | `W2043214237` | `inferred` | Marks inter-trial interval onset. |
