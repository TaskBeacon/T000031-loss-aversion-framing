from __future__ import annotations

from functools import partial
from typing import Any

from psyflow import StimUnit, set_trial_context

from .utils import CHOICE_GAMBLE, CHOICE_SAFE


def _deadline_s(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, (list, tuple)) and value:
        try:
            return float(max(value))
        except Exception:
            return None
    return None


def _as_duration(controller, value: Any, default_value: float) -> float:
    if hasattr(controller, "sample_duration"):
        return float(controller.sample_duration(value, default_value))
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, (list, tuple)) and value:
        try:
            return float(max(value))
        except Exception:
            return float(default_value)
    return float(default_value)


def _trial_id(controller) -> int:
    if hasattr(controller, "next_trial_id"):
        return int(controller.next_trial_id())
    return 1


def _task_dict(settings, attr_name: str) -> dict[str, Any]:
    value = getattr(settings, attr_name, {})
    return value if isinstance(value, dict) else {}


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    controller,
    trigger_runtime,
    block_id=None,
    block_idx=None,
):
    """Run one framing trial (fixation -> decision -> feedback -> iti)."""
    trial_id = _trial_id(controller)
    condition_name = str(getattr(controller, "parse_condition", lambda c: c)(condition)).strip().lower()
    block_label = str(block_id) if block_id is not None else "block_0"
    block_index = int(block_idx) if block_idx is not None else 0
    block_trial_index = int(getattr(controller, "trial_count_block", 0)) + 1

    safe_key = str(getattr(settings, "safe_key", "f")).strip().lower()
    gamble_key = str(getattr(settings, "gamble_key", "j")).strip().lower()
    response_keys = [safe_key, gamble_key]

    offer = controller.sample_offer(condition_name)
    fixation_duration = _as_duration(controller, settings.fixation_duration, 0.5)
    decision_deadline = float(getattr(settings, "decision_deadline", 4.0))
    feedback_duration = float(getattr(settings, "feedback_duration", 0.7))
    iti_duration = _as_duration(controller, settings.iti_duration, 0.5)

    trial_data = {
        "condition": condition_name,
        "block_id": block_label,
        "block_idx": block_index,
        "trial_id": trial_id,
        "trial_index": block_trial_index,
        "offer_id": str(offer.get("offer_id", "")),
    }

    make_unit = partial(StimUnit, win=win, kb=kb, runtime=trigger_runtime)

    fixation = make_unit(unit_label="fixation").add_stim(stim_bank.get("fixation"))
    set_trial_context(
        fixation,
        trial_id=trial_id,
        phase="fixation",
        deadline_s=_deadline_s(fixation_duration),
        valid_keys=[],
        block_id=block_label,
        condition_id=condition_name,
        task_factors={"stage": "fixation", "offer_id": trial_data["offer_id"], "block_idx": block_index},
        stim_id="fixation",
    )
    fixation.show(
        duration=fixation_duration,
        onset_trigger=settings.triggers.get("fixation_onset"),
    ).to_dict(trial_data)

    decision = make_unit(unit_label="decision")
    decision.add_stim(stim_bank.get_and_format("frame_label", frame_label=str(offer.get("frame_label", ""))))
    decision.add_stim(stim_bank.get_and_format("scenario_text", scenario_text=str(offer.get("scenario_text", ""))))
    decision.add_stim(stim_bank.get_and_format("safe_option_text", safe_option_text=str(offer.get("safe_text", ""))))
    decision.add_stim(
        stim_bank.get_and_format("gamble_option_text", gamble_option_text=str(offer.get("gamble_text", "")))
    )
    decision.add_stim(stim_bank.get_and_format("key_hint", safe_key=safe_key.upper(), gamble_key=gamble_key.upper()))
    set_trial_context(
        decision,
        trial_id=trial_id,
        phase="decision",
        deadline_s=_deadline_s(decision_deadline),
        valid_keys=response_keys,
        block_id=block_label,
        condition_id=condition_name,
        task_factors={
            "stage": "decision",
            "offer_id": trial_data["offer_id"],
            "safe_key": safe_key,
            "gamble_key": gamble_key,
            "block_idx": block_index,
        },
        stim_id="frame_label+scenario_text+safe_option_text+gamble_option_text+key_hint",
    )
    decision.capture_response(
        keys=response_keys,
        duration=decision_deadline,
        onset_trigger=settings.triggers.get("decision_onset"),
        response_trigger=None,
        timeout_trigger=settings.triggers.get("choice_timeout"),
    )
    decision.to_dict(trial_data)

    response_key = str(decision.get_state("response", "")).strip().lower()
    timed_out = response_key not in response_keys
    if timed_out:
        chosen_option = ""
        chose_gamble: bool | None = None
    elif response_key == safe_key:
        chosen_option = CHOICE_SAFE
        chose_gamble = False
        trigger_runtime.send(settings.triggers.get("choice_safe"))
    else:
        chosen_option = CHOICE_GAMBLE
        chose_gamble = True
        trigger_runtime.send(settings.triggers.get("choice_gamble"))

    choice_labels = _task_dict(settings, "choice_labels")
    feedback_template = str(getattr(settings, "feedback_choice_template", "{choice_label}"))
    safe_label = str(choice_labels.get(CHOICE_SAFE, CHOICE_SAFE))
    gamble_label = str(choice_labels.get(CHOICE_GAMBLE, CHOICE_GAMBLE))

    if timed_out:
        feedback_stim_id = "feedback_timeout"
        feedback_stim = stim_bank.get("feedback_timeout")
    else:
        choice_label = gamble_label if bool(chose_gamble) else safe_label
        chosen_text = feedback_template.format(choice_label=choice_label)
        feedback_stim_id = "feedback_choice"
        feedback_stim = stim_bank.get_and_format("feedback_choice", chosen_text=chosen_text)

    feedback = make_unit(unit_label="feedback").add_stim(feedback_stim)
    set_trial_context(
        feedback,
        trial_id=trial_id,
        phase="feedback",
        deadline_s=_deadline_s(feedback_duration),
        valid_keys=[],
        block_id=block_label,
        condition_id=condition_name,
        task_factors={
            "stage": "feedback",
            "offer_id": trial_data["offer_id"],
            "chosen_option": chosen_option,
            "timed_out": timed_out,
            "block_idx": block_index,
        },
        stim_id=feedback_stim_id,
    )
    feedback.show(
        duration=feedback_duration,
        onset_trigger=settings.triggers.get("feedback_onset"),
    ).to_dict(trial_data)

    iti = make_unit(unit_label="iti").add_stim(stim_bank.get("fixation"))
    set_trial_context(
        iti,
        trial_id=trial_id,
        phase="iti",
        deadline_s=_deadline_s(iti_duration),
        valid_keys=[],
        block_id=block_label,
        condition_id=condition_name,
        task_factors={"stage": "iti", "block_idx": block_index},
        stim_id="fixation",
    )
    iti.show(
        duration=iti_duration,
        onset_trigger=settings.triggers.get("iti_onset"),
    ).to_dict(trial_data)

    rt = decision.get_state("rt", None)
    rt_s = float(rt) if isinstance(rt, (int, float)) else None

    trial_data.update(
        {
            "response_key": response_key if not timed_out else "",
            "chosen_option": chosen_option,
            "timed_out": bool(timed_out),
            "rt_s": rt_s,
            "chose_gamble": bool(chose_gamble) if chose_gamble is not None else None,
            "safe_key": safe_key,
            "gamble_key": gamble_key,
            "frame_label": str(offer.get("frame_label", "")),
            "scenario_text": str(offer.get("scenario_text", "")),
            "safe_option_text": str(offer.get("safe_text", "")),
            "gamble_option_text": str(offer.get("gamble_text", "")),
            "ev_safe": float(offer.get("ev_safe", 0.0)),
            "ev_gamble": float(offer.get("ev_gamble", 0.0)),
            "endowment": float(offer.get("endowment", 0.0)),
            "sure_amount": float(offer.get("sure_amount", 0.0)),
            "gamble_gain": float(offer.get("gamble_gain", 0.0)),
            "gamble_loss": float(offer.get("gamble_loss", 0.0)),
            "gamble_gain_prob": float(offer.get("gamble_gain_prob", 0.0)),
        }
    )

    controller.record_trial(
        condition=condition_name,
        chose_gamble=chose_gamble,
        rt_s=rt_s,
        timed_out=bool(timed_out),
    )
    return trial_data
