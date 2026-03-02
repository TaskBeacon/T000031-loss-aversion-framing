from functools import partial
from pathlib import Path

import pandas as pd
from psychopy import core

from psyflow import (
    BlockUnit,
    StimBank,
    StimUnit,
    SubInfo,
    TaskRunOptions,
    TaskSettings,
    context_from_config,
    count_down,
    initialize_exp,
    initialize_triggers,
    load_config,
    parse_task_run_options,
    runtime_context,
)

from src import Controller, run_trial


def _make_qa_trigger_runtime():
    return initialize_triggers(mock=True)


MODES = ("human", "qa", "sim")
DEFAULT_CONFIG_BY_MODE = {
    "human": "config/config.yaml",
    "qa": "config/config_qa.yaml",
    "sim": "config/config_scripted_sim.yaml",
}


def _parse_args(task_root: Path) -> TaskRunOptions:
    return parse_task_run_options(
        task_root=task_root,
        description="Run Loss Aversion / Framing Task in human/qa/sim mode.",
        default_config_by_mode=DEFAULT_CONFIG_BY_MODE,
        modes=MODES,
    )


def _as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _as_float(value) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def _summarize_trials(trials: list[dict]) -> tuple[float, float, int]:
    if not trials:
        return 0.0, 0.0, 0

    timeout_count = sum(1 for row in trials if _as_bool(row.get("timed_out", False)))
    responded = [row for row in trials if not _as_bool(row.get("timed_out", False))]
    gamble_count = sum(1 for row in responded if _as_bool(row.get("chose_gamble", False)))
    gamble_rate = (gamble_count / len(responded)) if responded else 0.0

    rt_values = []
    for row in responded:
        rt = _as_float(row.get("rt_s", None))
        if rt is not None:
            rt_values.append(rt)
    mean_rt_ms = (sum(rt_values) / len(rt_values) * 1000.0) if rt_values else 0.0
    return gamble_rate, mean_rt_ms, timeout_count


def _condition_gamble_rates(trials: list[dict]) -> dict[str, float]:
    conds = ("gain_frame", "loss_frame", "mixed_frame")
    out = {cond: 0.0 for cond in conds}
    for cond in conds:
        rows = [r for r in trials if str(r.get("condition", "")) == cond and not _as_bool(r.get("timed_out", False))]
        if not rows:
            out[cond] = 0.0
            continue
        g = sum(1 for r in rows if _as_bool(r.get("chose_gamble", False)))
        out[cond] = g / len(rows)
    return out


def run(options: TaskRunOptions):
    task_root = Path(__file__).resolve().parent
    cfg = load_config(str(options.config_path))
    mode = options.mode

    ctx = None
    if mode in ("qa", "sim"):
        ctx = context_from_config(task_dir=task_root, config=cfg, mode=mode)
        sim_participant = "sim"
        if ctx.session is not None:
            sim_participant = str(ctx.session.participant_id or "sim")
        with runtime_context(ctx):
            _run_impl(mode=mode, output_dir=ctx.output_dir, cfg=cfg, participant_id=sim_participant)
    else:
        _run_impl(mode=mode, output_dir=None, cfg=cfg, participant_id="human")


def _run_impl(*, mode: str, output_dir: Path | None, cfg: dict, participant_id: str):
    if mode == "qa":
        subject_data = {"subject_id": "qa"}
    elif mode == "sim":
        subject_data = {"subject_id": participant_id}
    else:
        subform = SubInfo(cfg["subform_config"])
        subject_data = subform.collect()

    settings = TaskSettings.from_dict(cfg["task_config"])
    if mode in ("qa", "sim") and output_dir is not None:
        settings.save_path = str(output_dir)

    settings.add_subinfo(subject_data)

    if mode == "qa" and output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        settings.res_file = str(output_dir / "qa_trace.csv")
        settings.log_file = str(output_dir / "qa_psychopy.log")
        settings.json_file = str(output_dir / "qa_settings.json")

    settings.triggers = cfg["trigger_config"]
    if mode in ("qa", "sim"):
        trigger_runtime = _make_qa_trigger_runtime()
    else:
        trigger_runtime = initialize_triggers(cfg)

    win, kb = initialize_exp(settings)

    stim_bank = StimBank(win, cfg["stim_config"])
    if mode not in ("qa", "sim"):
        stim_bank = stim_bank.convert_to_voice("instruction_text")
    stim_bank = stim_bank.preload_all()

    settings.controller = cfg["controller_config"]
    settings.save_to_json()
    controller = Controller.from_dict(settings.controller)

    trigger_runtime.send(settings.triggers.get("exp_onset"))

    instr = StimUnit("instruction_text", win, kb, runtime=trigger_runtime).add_stim(
        stim_bank.get("instruction_text")
    )
    if mode not in ("qa", "sim"):
        instr.add_stim(stim_bank.get("instruction_text_voice"))
    instr.wait_and_continue()

    all_data: list[dict] = []
    total_blocks = int(getattr(settings, "total_blocks", 1))
    for block_i in range(total_blocks):
        controller.start_block(block_i)
        if mode not in ("qa", "sim"):
            count_down(win, 3, color="black")

        block = (
            BlockUnit(
                block_id=f"block_{block_i}",
                block_idx=block_i,
                settings=settings,
                window=win,
                keyboard=kb,
            )
            .generate_conditions()
            .on_start(lambda b: trigger_runtime.send(settings.triggers.get("block_onset")))
            .on_end(lambda b: trigger_runtime.send(settings.triggers.get("block_end")))
            .run_trial(
                partial(
                    run_trial,
                    stim_bank=stim_bank,
                    controller=controller,
                    trigger_runtime=trigger_runtime,
                    block_id=f"block_{block_i}",
                    block_idx=block_i,
                )
            )
            .to_dict(all_data)
        )

        block_trials = block.get_all_data()
        block_gamble_rate, block_rt_ms, block_timeouts = _summarize_trials(block_trials)
        if block_i < (total_blocks - 1):
            StimUnit("block", win, kb, runtime=trigger_runtime).add_stim(
                stim_bank.get_and_format(
                    "block_break",
                    block_num=block_i + 1,
                    total_blocks=total_blocks,
                    block_gamble_rate=block_gamble_rate,
                    mean_rt_ms=block_rt_ms,
                    timeout_count=block_timeouts,
                )
            ).wait_and_continue()

    overall_gamble_rate, overall_rt_ms, overall_timeouts = _summarize_trials(all_data)
    cond_rates = _condition_gamble_rates(all_data)

    StimUnit("goodbye", win, kb, runtime=trigger_runtime).add_stim(
        stim_bank.get_and_format(
            "good_bye",
            total_trials=len(all_data),
            overall_gamble_rate=overall_gamble_rate,
            mean_rt_ms=overall_rt_ms,
            timeout_count=overall_timeouts,
            gain_rate=cond_rates.get("gain_frame", 0.0),
            loss_rate=cond_rates.get("loss_frame", 0.0),
            mixed_rate=cond_rates.get("mixed_frame", 0.0),
        )
    ).wait_and_continue(terminate=True)

    trigger_runtime.send(settings.triggers.get("exp_end"))

    pd.DataFrame(all_data).to_csv(settings.res_file, index=False)

    trigger_runtime.close()
    core.quit()


def main() -> None:
    task_root = Path(__file__).resolve().parent
    options = _parse_args(task_root)
    run(options)


if __name__ == "__main__":
    main()
