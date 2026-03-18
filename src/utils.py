from __future__ import annotations

import hashlib
import random
from typing import Any

from psychopy import logging

COND_GAIN = "gain_frame"
COND_LOSS = "loss_frame"
COND_MIXED = "mixed_frame"

CHOICE_SAFE = "safe"
CHOICE_GAMBLE = "gamble"


def normalize_condition(condition: Any) -> str:
    token = str(condition or "").strip().lower()
    if token in {COND_GAIN, COND_LOSS, COND_MIXED}:
        return token
    raise ValueError(f"Unsupported framing condition: {condition!r}")


def _to_float(value: Any, fallback: float) -> float:
    try:
        parsed = float(value)
    except Exception:
        return float(fallback)
    return parsed if parsed == parsed else float(fallback)


def _to_int(value: Any, fallback: int) -> int:
    return int(round(_to_float(value, float(fallback))))


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _pct_text(prob: float) -> int:
    return round(_clamp01(prob) * 100)


def _amount_text(amount: float) -> str:
    rounded = round(float(amount))
    if rounded >= 0:
        return f"获得 {rounded} 元"
    return f"损失 {abs(rounded)} 元"


def _stable_seed(*parts: Any) -> int:
    payload = "|".join(str(part) for part in parts)
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def _offer_banks(settings: Any) -> dict[str, list[dict[str, Any]]]:
    banks = getattr(settings, "offer_banks", None)
    if not isinstance(banks, dict):
        raise ValueError("task.offer_banks must be a mapping keyed by condition.")

    normalized: dict[str, list[dict[str, Any]]] = {}
    for condition in (COND_GAIN, COND_LOSS, COND_MIXED):
        value = banks.get(condition)
        if not isinstance(value, list) or not value:
            raise ValueError(f"task.offer_banks must define a non-empty list for {condition!r}.")
        cleaned: list[dict[str, Any]] = []
        for item in value:
            if isinstance(item, dict):
                cleaned.append(dict(item))
        if not cleaned:
            raise ValueError(f"task.offer_banks[{condition!r}] does not contain any offer objects.")
        normalized[condition] = cleaned
    return normalized


def _sample_offer_row(settings: Any, condition: str, *, block_idx: int, trial_id: int) -> dict[str, Any]:
    cond = normalize_condition(condition)
    banks = _offer_banks(settings)
    block_seed = getattr(settings, "block_seed", None)
    base_seed = None
    if isinstance(block_seed, list) and 0 <= block_idx < len(block_seed):
        base_seed = block_seed[block_idx]
    if base_seed is None:
        base_seed = getattr(settings, "overall_seed", 2025)

    rng = random.Random(_stable_seed(base_seed, cond, block_idx, trial_id))
    return dict(rng.choice(banks[cond]))


def sample_offer(settings: Any, condition: str, *, block_idx: int, trial_id: int) -> dict[str, Any]:
    cond = normalize_condition(condition)
    row = _sample_offer_row(settings, cond, block_idx=block_idx, trial_id=trial_id)

    if cond == COND_GAIN:
        endowment = _to_int(row.get("endowment"), 100)
        sure_keep = _to_int(row.get("sure_keep"), 80)
        gamble_keep = _to_int(row.get("gamble_keep"), endowment)
        gamble_prob = _clamp01(_to_float(row.get("gamble_prob"), 0.8))
        keep_pct = _pct_text(gamble_prob)
        zero_pct = 100 - keep_pct
        offer = {
            "condition": cond,
            "offer_id": str(row.get("offer_id") or f"gain_{endowment}_{sure_keep}_{keep_pct}"),
            "frame_label": "收益框架",
            "scenario_text": f"你获得 {endowment} 元预算。请选择其一：",
            "safe_text": f"方案A（确定）\n保留 {sure_keep} 元",
            "gamble_text": f"方案B（风险）\n{keep_pct}% 保留 {gamble_keep} 元\n{zero_pct}% 保留 0 元",
            "ev_safe": float(sure_keep),
            "ev_gamble": float(gamble_prob * gamble_keep),
            "endowment": float(endowment),
            "sure_amount": float(sure_keep),
            "gamble_gain": float(gamble_keep),
            "gamble_loss": 0.0,
            "gamble_gain_prob": float(gamble_prob),
        }
    elif cond == COND_LOSS:
        endowment = _to_int(row.get("endowment"), 100)
        sure_loss = _to_int(row.get("sure_loss"), 20)
        gamble_loss = _to_int(row.get("gamble_loss"), endowment)
        gamble_loss_prob = _clamp01(_to_float(row.get("gamble_loss_prob"), 0.2))
        no_loss_prob = 1.0 - gamble_loss_prob
        loss_pct = _pct_text(gamble_loss_prob)
        keep_pct = _pct_text(no_loss_prob)
        offer = {
            "condition": cond,
            "offer_id": str(row.get("offer_id") or f"loss_{endowment}_{sure_loss}_{loss_pct}"),
            "frame_label": "损失框架",
            "scenario_text": f"你获得 {endowment} 元预算。请选择其一：",
            "safe_text": f"方案A（确定）\n损失 {sure_loss} 元",
            "gamble_text": f"方案B（风险）\n{keep_pct}% 损失 0 元\n{loss_pct}% 损失 {gamble_loss} 元",
            "ev_safe": float(-sure_loss),
            "ev_gamble": float(-gamble_loss_prob * gamble_loss),
            "endowment": float(endowment),
            "sure_amount": float(-sure_loss),
            "gamble_gain": 0.0,
            "gamble_loss": float(gamble_loss),
            "gamble_gain_prob": float(no_loss_prob),
        }
    else:
        sure_amount = _to_float(row.get("sure_amount"), 0.0)
        gamble_gain = _to_float(row.get("gamble_gain"), 40.0)
        gamble_loss = _to_float(row.get("gamble_loss"), 30.0)
        gain_prob = _clamp01(_to_float(row.get("gamble_gain_prob"), 0.5))
        loss_prob = 1.0 - gain_prob
        gain_pct = _pct_text(gain_prob)
        loss_pct = _pct_text(loss_prob)
        offer = {
            "condition": cond,
            "offer_id": str(row.get("offer_id") or f"mixed_{round(gamble_gain)}_{round(gamble_loss)}_{gain_pct}"),
            "frame_label": "混合框架",
            "scenario_text": "请选择其一：",
            "safe_text": f"方案A（确定）\n{_amount_text(sure_amount)}",
            "gamble_text": f"方案B（风险）\n{gain_pct}% 获得 {round(gamble_gain)} 元\n{loss_pct}% 损失 {round(gamble_loss)} 元",
            "ev_safe": float(sure_amount),
            "ev_gamble": float(gain_prob * gamble_gain - loss_prob * gamble_loss),
            "endowment": 0.0,
            "sure_amount": float(sure_amount),
            "gamble_gain": float(gamble_gain),
            "gamble_loss": float(gamble_loss),
            "gamble_gain_prob": float(gain_prob),
        }

    if bool(getattr(settings, "enable_logging", True)):
        trial_per_block = int(getattr(settings, "trials_per_block", getattr(settings, "trial_per_block", 1)) or 1)
        block_trial_index = ((int(trial_id) - 1) % trial_per_block) + 1 if trial_id is not None else 0
        logging.data(
            "[Framing] "
            f"trial_id={trial_id} block_idx={block_idx} condition={cond} "
            f"offer_id={offer['offer_id']} block_trial={block_trial_index}"
        )

    return offer


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    token = str(value or "").strip().lower()
    return token in {"1", "true", "yes", "y"}


def _as_number(value: Any) -> float | None:
    try:
        parsed = float(value)
    except Exception:
        return None
    return parsed if parsed == parsed else None


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _format_percent(value01: float) -> str:
    return f"{value01 * 100:.1f}%"


def _summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "gamble_rate": "0.0%",
            "mean_rt_ms": "0",
            "timeout_count": 0,
            "total_trials": 0,
        }

    timeout_count = sum(1 for row in rows if _as_bool(row.get("timed_out", False)))
    responded = [row for row in rows if not _as_bool(row.get("timed_out", False))]
    gamble_count = sum(1 for row in responded if _as_bool(row.get("chose_gamble", False)))
    gamble_rate = _format_percent(gamble_count / len(responded)) if responded else "0.0%"
    rt_values = [_as_number(row.get("rt_s")) for row in responded]
    rt_values = [value for value in rt_values if value is not None]
    mean_rt_ms = str(round(_mean([float(value) for value in rt_values]) * 1000))

    return {
        "gamble_rate": gamble_rate,
        "mean_rt_ms": mean_rt_ms,
        "timeout_count": timeout_count,
        "total_trials": len(rows),
    }


def summarize_block(rows: list[dict[str, Any]], block_id: str) -> dict[str, Any]:
    block_rows = [row for row in rows if str(row.get("block_id", "")) == block_id]
    return _summarize_rows(block_rows)


def summarize_overall(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return _summarize_rows(rows)


def _condition_rate(rows: list[dict[str, Any]], condition: str) -> str:
    cond_rows = [row for row in rows if str(row.get("condition", "")) == condition and not _as_bool(row.get("timed_out", False))]
    if not cond_rows:
        return "0.0%"
    gamble_count = sum(1 for row in cond_rows if _as_bool(row.get("chose_gamble", False)))
    return _format_percent(gamble_count / len(cond_rows))


def summarize_condition_rates(rows: list[dict[str, Any]]) -> dict[str, str]:
    return {
        "gain_rate": _condition_rate(rows, COND_GAIN),
        "loss_rate": _condition_rate(rows, COND_LOSS),
        "mixed_rate": _condition_rate(rows, COND_MIXED),
    }
