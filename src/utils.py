from __future__ import annotations

import random
from typing import Any

from psychopy import logging

COND_GAIN = "gain_frame"
COND_LOSS = "loss_frame"
COND_MIXED = "mixed_frame"

CHOICE_SAFE = "safe"
CHOICE_GAMBLE = "gamble"


class Controller:
    """Trial sampler and performance tracker for framing/loss-aversion choices."""

    def __init__(
        self,
        fixation_duration: list[float] | tuple[float, ...] | float = (0.4, 0.7),
        decision_deadline: float = 4.0,
        feedback_duration: float = 0.7,
        iti_duration: list[float] | tuple[float, ...] | float = (0.4, 0.8),
        gain_trials: list[dict[str, Any]] | None = None,
        loss_trials: list[dict[str, Any]] | None = None,
        mixed_trials: list[dict[str, Any]] | None = None,
        random_seed: int | None = None,
        enable_logging: bool = True,
    ):
        self.fixation_duration = fixation_duration
        self.decision_deadline = max(0.2, float(decision_deadline))
        self.feedback_duration = max(0.1, float(feedback_duration))
        self.iti_duration = iti_duration
        self.enable_logging = bool(enable_logging)
        self.rng = random.Random(random_seed)

        self.gain_trials = self._normalize_trial_list(gain_trials, self._default_gain_trials())
        self.loss_trials = self._normalize_trial_list(loss_trials, self._default_loss_trials())
        self.mixed_trials = self._normalize_trial_list(mixed_trials, self._default_mixed_trials())

        self.block_idx = -1
        self.trial_count_total = 0
        self.trial_count_block = 0

        self.total_bucket = self._new_bucket()
        self.block_bucket = self._new_bucket()
        self.cond_total = {COND_GAIN: self._new_bucket(), COND_LOSS: self._new_bucket(), COND_MIXED: self._new_bucket()}
        self.cond_block = {COND_GAIN: self._new_bucket(), COND_LOSS: self._new_bucket(), COND_MIXED: self._new_bucket()}

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> "Controller":
        cfg = dict(config or {})
        return cls(
            fixation_duration=cfg.get("fixation_duration", (0.4, 0.7)),
            decision_deadline=cfg.get("decision_deadline", 4.0),
            feedback_duration=cfg.get("feedback_duration", 0.7),
            iti_duration=cfg.get("iti_duration", (0.4, 0.8)),
            gain_trials=cfg.get("gain_trials", None),
            loss_trials=cfg.get("loss_trials", None),
            mixed_trials=cfg.get("mixed_trials", None),
            random_seed=cfg.get("random_seed", None),
            enable_logging=bool(cfg.get("enable_logging", True)),
        )

    @staticmethod
    def _new_bucket() -> dict[str, float]:
        return {"n": 0, "gamble": 0, "timeouts": 0, "rt_sum": 0.0, "rt_n": 0}

    @staticmethod
    def _normalize_trial_list(value: Any, fallback: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return list(fallback)
        clean: list[dict[str, Any]] = []
        for item in value:
            if isinstance(item, dict):
                clean.append(dict(item))
        return clean or list(fallback)

    @staticmethod
    def _default_gain_trials() -> list[dict[str, Any]]:
        return [
            {"offer_id": "gain_100_80", "endowment": 100, "sure_keep": 80, "gamble_keep": 100, "gamble_prob": 0.8},
            {"offer_id": "gain_100_60", "endowment": 100, "sure_keep": 60, "gamble_keep": 100, "gamble_prob": 0.6},
            {"offer_id": "gain_120_72", "endowment": 120, "sure_keep": 72, "gamble_keep": 120, "gamble_prob": 0.6},
            {"offer_id": "gain_150_105", "endowment": 150, "sure_keep": 105, "gamble_keep": 150, "gamble_prob": 0.7},
        ]

    @staticmethod
    def _default_loss_trials() -> list[dict[str, Any]]:
        return [
            {"offer_id": "loss_100_20", "endowment": 100, "sure_loss": 20, "gamble_loss": 100, "gamble_loss_prob": 0.2},
            {"offer_id": "loss_100_40", "endowment": 100, "sure_loss": 40, "gamble_loss": 100, "gamble_loss_prob": 0.4},
            {"offer_id": "loss_120_36", "endowment": 120, "sure_loss": 36, "gamble_loss": 120, "gamble_loss_prob": 0.3},
            {"offer_id": "loss_150_45", "endowment": 150, "sure_loss": 45, "gamble_loss": 150, "gamble_loss_prob": 0.3},
        ]

    @staticmethod
    def _default_mixed_trials() -> list[dict[str, Any]]:
        return [
            {"offer_id": "mixed_40_30", "sure_amount": 0, "gamble_gain": 40, "gamble_loss": 30, "gamble_gain_prob": 0.5},
            {"offer_id": "mixed_60_45", "sure_amount": 0, "gamble_gain": 60, "gamble_loss": 45, "gamble_gain_prob": 0.5},
            {"offer_id": "mixed_30_20", "sure_amount": 0, "gamble_gain": 30, "gamble_loss": 20, "gamble_gain_prob": 0.4},
            {"offer_id": "mixed_70_50", "sure_amount": 10, "gamble_gain": 70, "gamble_loss": 50, "gamble_gain_prob": 0.5},
        ]

    @staticmethod
    def parse_condition(condition: str) -> str:
        token = str(condition).strip().lower()
        if token in {COND_GAIN, COND_LOSS, COND_MIXED}:
            return token
        raise ValueError(f"Unsupported framing condition: {condition!r}")

    def start_block(self, block_idx: int) -> None:
        self.block_idx = int(block_idx)
        self.trial_count_block = 0
        self.block_bucket = self._new_bucket()
        self.cond_block = {COND_GAIN: self._new_bucket(), COND_LOSS: self._new_bucket(), COND_MIXED: self._new_bucket()}

    def next_trial_id(self) -> int:
        return int(self.trial_count_total) + 1

    def sample_duration(self, value: Any, default: float) -> float:
        if isinstance(value, (int, float)):
            return max(0.0, float(value))
        if isinstance(value, (list, tuple)) and len(value) >= 2:
            try:
                low = float(value[0])
                high = float(value[1])
            except Exception:
                return max(0.0, float(default))
            if high < low:
                low, high = high, low
            return max(0.0, float(self.rng.uniform(low, high)))
        return max(0.0, float(default))

    @staticmethod
    def _pct_text(prob: float) -> int:
        return int(round(max(0.0, min(1.0, float(prob))) * 100))

    @staticmethod
    def _amount_text(amount: float) -> str:
        val = int(round(float(amount)))
        if val >= 0:
            return f"获得 {val} 元"
        return f"损失 {abs(val)} 元"

    def sample_offer(self, condition: str) -> dict[str, Any]:
        cond = self.parse_condition(condition)

        if cond == COND_GAIN:
            row = dict(self.rng.choice(self.gain_trials))
            endowment = int(row.get("endowment", 100))
            sure_keep = int(row.get("sure_keep", 80))
            gamble_keep = int(row.get("gamble_keep", endowment))
            gamble_prob = max(0.0, min(1.0, float(row.get("gamble_prob", 0.8))))
            keep_pct = self._pct_text(gamble_prob)
            zero_pct = 100 - keep_pct
            ev_safe = float(sure_keep)
            ev_gamble = float(gamble_prob * gamble_keep)
            return {
                "condition": COND_GAIN,
                "offer_id": str(row.get("offer_id", f"gain_{endowment}_{sure_keep}_{keep_pct}")),
                "frame_label": "收益框架",
                "scenario_text": f"你获得 {endowment} 元预算。请选择其一：",
                "safe_text": f"方案A（确定）\n保留 {sure_keep} 元",
                "gamble_text": f"方案B（风险）\n{keep_pct}% 保留 {gamble_keep} 元\n{zero_pct}% 保留 0 元",
                "ev_safe": ev_safe,
                "ev_gamble": ev_gamble,
                "endowment": endowment,
                "sure_amount": sure_keep,
                "gamble_gain": gamble_keep,
                "gamble_loss": 0,
                "gamble_gain_prob": gamble_prob,
            }

        if cond == COND_LOSS:
            row = dict(self.rng.choice(self.loss_trials))
            endowment = int(row.get("endowment", 100))
            sure_loss = int(row.get("sure_loss", 20))
            gamble_loss = int(row.get("gamble_loss", endowment))
            loss_prob = max(0.0, min(1.0, float(row.get("gamble_loss_prob", 0.2))))
            no_loss_prob = 1.0 - loss_prob
            loss_pct = self._pct_text(loss_prob)
            keep_pct = self._pct_text(no_loss_prob)
            ev_safe = float(-sure_loss)
            ev_gamble = float(-loss_prob * gamble_loss)
            return {
                "condition": COND_LOSS,
                "offer_id": str(row.get("offer_id", f"loss_{endowment}_{sure_loss}_{loss_pct}")),
                "frame_label": "损失框架",
                "scenario_text": f"你获得 {endowment} 元预算。请选择其一：",
                "safe_text": f"方案A（确定）\n损失 {sure_loss} 元",
                "gamble_text": f"方案B（风险）\n{keep_pct}% 损失 0 元\n{loss_pct}% 损失 {gamble_loss} 元",
                "ev_safe": ev_safe,
                "ev_gamble": ev_gamble,
                "endowment": endowment,
                "sure_amount": -sure_loss,
                "gamble_gain": 0,
                "gamble_loss": gamble_loss,
                "gamble_gain_prob": no_loss_prob,
            }

        row = dict(self.rng.choice(self.mixed_trials))
        sure_amount = float(row.get("sure_amount", 0))
        gamble_gain = float(row.get("gamble_gain", 40))
        gamble_loss = float(row.get("gamble_loss", 30))
        gain_prob = max(0.0, min(1.0, float(row.get("gamble_gain_prob", 0.5))))
        loss_prob = 1.0 - gain_prob
        gain_pct = self._pct_text(gain_prob)
        loss_pct = self._pct_text(loss_prob)
        ev_safe = float(sure_amount)
        ev_gamble = float(gain_prob * gamble_gain - loss_prob * gamble_loss)
        return {
            "condition": COND_MIXED,
            "offer_id": str(row.get("offer_id", f"mixed_{int(gamble_gain)}_{int(gamble_loss)}_{gain_pct}")),
            "frame_label": "混合框架",
            "scenario_text": "请选择其一：",
            "safe_text": f"方案A（确定）\n{self._amount_text(sure_amount)}",
            "gamble_text": f"方案B（风险）\n{gain_pct}% 获得 {int(round(gamble_gain))} 元\n{loss_pct}% 损失 {int(round(gamble_loss))} 元",
            "ev_safe": ev_safe,
            "ev_gamble": ev_gamble,
            "endowment": 0,
            "sure_amount": sure_amount,
            "gamble_gain": gamble_gain,
            "gamble_loss": gamble_loss,
            "gamble_gain_prob": gain_prob,
        }

    def record_trial(
        self,
        *,
        condition: str,
        chose_gamble: bool | None,
        rt_s: float | None,
        timed_out: bool,
    ) -> None:
        cond = self.parse_condition(condition)
        self.trial_count_total += 1
        self.trial_count_block += 1

        for bucket in (self.total_bucket, self.block_bucket, self.cond_total[cond], self.cond_block[cond]):
            bucket["n"] += 1
            if timed_out:
                bucket["timeouts"] += 1
            if bool(chose_gamble):
                bucket["gamble"] += 1
            if (rt_s is not None) and (not timed_out):
                rt = max(0.0, float(rt_s))
                bucket["rt_sum"] += rt
                bucket["rt_n"] += 1

        if self.enable_logging:
            logging.data(
                f"[Framing] block={self.block_idx} trial_block={self.trial_count_block} "
                f"trial_total={self.trial_count_total} condition={cond} "
                f"chose_gamble={chose_gamble} timed_out={timed_out} rt={rt_s}"
            )

    @staticmethod
    def _bucket_metrics(bucket: dict[str, float]) -> dict[str, float]:
        n = int(bucket.get("n", 0))
        gamble = int(bucket.get("gamble", 0))
        timeouts = int(bucket.get("timeouts", 0))
        rt_n = int(bucket.get("rt_n", 0))
        rt_sum = float(bucket.get("rt_sum", 0.0))
        responded_n = max(0, n - timeouts)
        gamble_rate = (gamble / responded_n) if responded_n > 0 else 0.0
        timeout_rate = (timeouts / n) if n > 0 else 0.0
        mean_rt_ms = (rt_sum / rt_n * 1000.0) if rt_n > 0 else 0.0
        return {
            "n": n,
            "gamble": gamble,
            "timeouts": timeouts,
            "responded_n": responded_n,
            "gamble_rate": gamble_rate,
            "timeout_rate": timeout_rate,
            "mean_rt_ms": mean_rt_ms,
        }

    def total_metrics(self) -> dict[str, float]:
        return self._bucket_metrics(self.total_bucket)

    def block_metrics(self) -> dict[str, float]:
        return self._bucket_metrics(self.block_bucket)

    def condition_metrics(self, condition: str, *, block_level: bool = False) -> dict[str, float]:
        cond = self.parse_condition(condition)
        bucket = self.cond_block[cond] if block_level else self.cond_total[cond]
        return self._bucket_metrics(bucket)
