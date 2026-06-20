from __future__ import annotations

from typing import Any

from psyflow import StimUnit, next_trial_id, set_trial_context

from .utils import CHOICE_GAMBLE, CHOICE_SAFE, normalize_condition


def _task_dict(settings: Any, attr_name: str) -> dict[str, Any]:
    value = getattr(settings, attr_name, {})
    return value if isinstance(value, dict) else {}


def _normalize_key(value: Any) -> str:
    return str(value or "").strip().lower()


def _as_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except Exception:
        return None
    return parsed if parsed == parsed else None


def _trigger_code(trigger_map: dict[str, Any], key: str, default: int) -> int:
    try:
        value = trigger_map.get(key, default)
        return int(value)
    except Exception:
        return int(default)


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    trigger_runtime,
    block_id=None,
    block_idx=None,
):
    """Run one framing trial (fixation -> decision -> feedback -> iti)."""
    trial_id = next_trial_id()
    if not isinstance(condition, dict) or "offer" not in condition:
        raise ValueError("Framing run_trial requires a scheduled condition dict with an offer.")
    condition_name = normalize_condition(condition.get("condition"))
    offer = dict(condition["offer"])
    block_label = str(block_id) if block_id is not None else "block_0"
    block_index = int(block_idx) if block_idx is not None else 0
    trial_per_block = int(getattr(settings, "trials_per_block", getattr(settings, "trial_per_block", 1)) or 1)
    block_trial_index = ((trial_id - 1) % trial_per_block) + 1

    safe_key = str(getattr(settings, "safe_key", "f")).strip().lower()
    gamble_key = str(getattr(settings, "gamble_key", "j")).strip().lower()
    response_keys = [safe_key, gamble_key]
    choice_labels = _task_dict(settings, "choice_labels")
    safe_label = str(choice_labels.get(CHOICE_SAFE, CHOICE_SAFE))
    gamble_label = str(choice_labels.get(CHOICE_GAMBLE, CHOICE_GAMBLE))
    feedback_template = str(getattr(settings, "feedback_choice_template", "你选择了 {choice_label}"))
    trigger_map = _task_dict(settings, "triggers")
    fixation_onset = _trigger_code(trigger_map, "fixation_onset", 20)
    decision_onset = _trigger_code(trigger_map, "decision_onset", 30)
    choice_safe_trigger = _trigger_code(trigger_map, "choice_safe", 31)
    choice_gamble_trigger = _trigger_code(trigger_map, "choice_gamble", 32)
    choice_timeout_trigger = _trigger_code(trigger_map, "choice_timeout", 33)
    feedback_onset = _trigger_code(trigger_map, "feedback_onset", 40)
    iti_onset = _trigger_code(trigger_map, "iti_onset", 50)

    fixation_duration = getattr(settings, "fixation_duration", 0.5)
    decision_deadline = getattr(settings, "decision_deadline", 4.0)
    feedback_duration = getattr(settings, "feedback_duration", 0.7)
    iti_duration = getattr(settings, "iti_duration", 0.5)

    trial_data = {
        "condition": condition_name,
        "block_id": block_label,
        "block_idx": block_index,
        "trial_id": trial_id,
        "trial_index": block_trial_index,
        "offer_id": str(offer.get("offer_id", "")),
    }

    fixation = StimUnit("fixation", win, kb, runtime=trigger_runtime).add_stim(stim_bank.get("fixation"))
    set_trial_context(
        fixation,
        trial_id=trial_id,
        phase="fixation",
        deadline_s=fixation_duration,
        valid_keys=[],
        block_id=block_label,
        condition_id=condition_name,
        task_factors={
            "stage": "fixation",
            "offer_id": trial_data["offer_id"],
            "block_idx": block_index,
            "trial_id": trial_id,
        },
        stim_id="fixation",
    )
    fixation.show(duration=fixation_duration, onset_trigger=fixation_onset).to_dict(trial_data)

    decision = StimUnit("decision", win, kb, runtime=trigger_runtime)
    decision.add_stim(
        stim_bank.get_and_format(
            "frame_label",
            frame_label=str(offer.get("frame_label", "")),
        )
    )
    decision.add_stim(
        stim_bank.get_and_format(
            "scenario_text",
            scenario_text=str(offer.get("scenario_text", "")),
        )
    )
    decision.add_stim(
        stim_bank.get_and_format(
            "safe_option_text",
            safe_option_text=str(offer.get("safe_text", "")),
        )
    )
    decision.add_stim(
        stim_bank.get_and_format(
            "gamble_option_text",
            gamble_option_text=str(offer.get("gamble_text", "")),
        )
    )
    decision.add_stim(
        stim_bank.get_and_format(
            "key_hint",
            safe_key=safe_key.upper(),
            gamble_key=gamble_key.upper(),
        )
    )
    set_trial_context(
        decision,
        trial_id=trial_id,
        phase="decision",
        deadline_s=decision_deadline,
        valid_keys=response_keys,
        block_id=block_label,
        condition_id=condition_name,
        task_factors={
            "stage": "decision",
            "offer_id": trial_data["offer_id"],
            "safe_key": safe_key,
            "gamble_key": gamble_key,
            "block_idx": block_index,
            "trial_id": trial_id,
        },
        stim_id="frame_label+scenario_text+safe_option_text+gamble_option_text+key_hint",
    )
    decision.capture_response(
        keys=response_keys,
        correct_keys=response_keys,
        duration=decision_deadline,
        response_trigger={
            safe_key: choice_safe_trigger,
            gamble_key: choice_gamble_trigger,
        },
        onset_trigger=decision_onset,
        timeout_trigger=choice_timeout_trigger,
    ).to_dict(trial_data)

    response_key = _normalize_key(decision.get_state("response", ""))
    timed_out = response_key not in response_keys
    if timed_out:
        chosen_option = ""
        chose_gamble: bool | None = None
        feedback_stim = stim_bank.get("feedback_timeout")
    elif response_key == safe_key:
        chosen_option = CHOICE_SAFE
        chose_gamble = False
        chosen_text = feedback_template.replace("{choice_label}", safe_label)
        feedback_stim = stim_bank.get_and_format("feedback_choice", chosen_text=chosen_text)
    else:
        chosen_option = CHOICE_GAMBLE
        chose_gamble = True
        chosen_text = feedback_template.replace("{choice_label}", gamble_label)
        feedback_stim = stim_bank.get_and_format("feedback_choice", chosen_text=chosen_text)

    rt_value = decision.get_state("rt", None)
    rt_s = _as_float(rt_value)

    feedback = StimUnit("feedback", win, kb, runtime=trigger_runtime).add_stim(feedback_stim)
    set_trial_context(
        feedback,
        trial_id=trial_id,
        phase="feedback",
        deadline_s=feedback_duration,
        valid_keys=[],
        block_id=block_label,
        condition_id=condition_name,
        task_factors={
            "stage": "feedback",
            "offer_id": trial_data["offer_id"],
            "chosen_option": chosen_option,
            "timed_out": timed_out,
            "block_idx": block_index,
            "trial_id": trial_id,
        },
        stim_id="feedback_timeout" if timed_out else "feedback_choice",
    )
    feedback.show(duration=feedback_duration, onset_trigger=feedback_onset).to_dict(trial_data)

    iti = StimUnit("iti", win, kb, runtime=trigger_runtime).add_stim(stim_bank.get("fixation"))
    set_trial_context(
        iti,
        trial_id=trial_id,
        phase="iti",
        deadline_s=iti_duration,
        valid_keys=[],
        block_id=block_label,
        condition_id=condition_name,
        task_factors={
            "stage": "iti",
            "block_idx": block_index,
            "trial_id": trial_id,
        },
        stim_id="fixation",
    )
    iti.show(duration=iti_duration, onset_trigger=iti_onset).to_dict(trial_data)

    trial_data.update(
        {
            "response_key": response_key if not timed_out else "",
            "chosen_option": chosen_option,
            "timed_out": bool(timed_out),
            "rt_s": rt_s,
            "chose_gamble": chose_gamble,
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
    return trial_data
