# Task Plot Review

## Evidence Match

- Pass: title and construct match the Loss Aversion / Framing Task.
- Pass: rows match configured gain_frame, loss_frame, and mixed_frame conditions.
- Pass: phase order matches README and `src/run_trial.py`: Fixation -> Decision -> Feedback -> ITI.
- Pass: timing labels match config: 400-700 ms fixation, 4000 ms decision, 700 ms feedback, 400-800 ms ITI.
- Pass: decision mapping shows F=safe and J=gamble.
- Pass: decision content distinguishes gain, loss, and mixed framing offers.
- Pass: feedback is shown as chosen option or timeout acknowledgement without inventing lottery-resolution feedback.

## Visual Quality

- Pass: labels and timings are readable.
- Pass: generated timeline content stays below the header band.
- Pass: fixed title and Construct subtitle are centered.
- Pass: top-right TaskBeacon logo lockup is borderless and non-overlapping.
- Pass: no generated title, logo, watermark, people, devices, or decorative scene is present.

## README Embed

- Pass: `README.md` contains `## 2. Task Flow`.
- Pass: the section embeds `![Task Flow](task_flow.png)`.
- Pass: final image is saved as `task_flow.png`; raw timeline is saved as `references/task_plot_timeline_raw.png`.
