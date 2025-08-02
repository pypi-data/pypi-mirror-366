import time
import math

__version__ = "2.2.0"
__author__ = "M.1XT"
__license__ = "R3"

_SCALE_FACTORS = {
    "s": 1_000_000_000,
    "ms": 1_000_000,
    "us": 1_000,
    "ns": 1,
    "ps": 1e-3,
    "fs": 1e-6
    # deliberately excluding "as", "zs", "ys"
}


class __ZIntTime:
    def __init__(self, res_scale=10**12):
        self.zunit = self.__discover_zunit()
        self.res_scale = res_scale
        self.ticks = 0
        self.remainder = 0
        self.last = time.perf_counter()

    def __discover_zunit(self, max_iter=1_000_000):
        last = time.perf_counter()
        min_diff = float("inf")
        for _ in range(max_iter):
            now = time.perf_counter()
            diff = now - last
            if 0 < diff < min_diff:
                min_diff = diff
            last = now
        return min_diff

    def update(self):
        now = time.perf_counter()
        elapsed = now - self.last
        self.last = now

        zunits = int(elapsed // self.zunit)
        fraction = elapsed - (zunits * self.zunit)

        self.ticks += zunits
        self.remainder += int(fraction / self.zunit * self.res_scale)

        if self.remainder >= self.res_scale:
            self.ticks += 1
            self.remainder -= self.res_scale

    def current_time(self):
        return self.ticks * self.zunit + (self.remainder * self.zunit / self.res_scale)


class __ARENA:
    def __init__(self, sample_size=5000, smoothing=0.95):
        self.last = time.perf_counter()
        self.samples = []
        self.smoothing = smoothing
        self.score = 0.0
        self.min_as_estimate = None
        self.stability_count = 0
        self.sample_size = sample_size

    def probe(self):
        now = time.perf_counter()
        gap = now - self.last
        self.last = now
        if len(self.samples) > 0:
            gap = (self.samples[-1] * self.smoothing) + (gap * (1 - self.smoothing))
        self.samples.append(gap)
        if len(self.samples) > self.sample_size:
            self.samples.pop(0)

    def infer_as_unit(self):
        if len(self.samples) < 3:
            return None
        diffs = [abs(self.samples[i+1] - self.samples[i]) for i in range(len(self.samples)-1)]
        refined = [d for d in diffs if d > 0]
        if not refined:
            return None

        min_diff = min(refined)
        variance = sum((d - min_diff) ** 2 for d in refined) / len(refined)
        score = 1.0 / (1.0 + variance * 1e24)  # كلما اقتربت من الثبات زاد الاقتراب من 1
        self.score = max(self.score * 0.9, score)  # تعزيز ناعم للتقييم

        # الثبات = عدد المرات التي تكررت فيها نفس القيمة الدنيا تقريبًا
        margin = min_diff * 0.05
        close_count = sum(1 for d in refined if abs(d - min_diff) < margin)
        self.stability_count = close_count
        self.min_as_estimate = min_diff

        return min_diff * 1e18  # التحويل إلى attosecond

    def reliability(self):
        if not self.min_as_estimate:
            return 0.0
        base = self.score
        stability_ratio = self.stability_count / max(1, len(self.samples))
        return round(min(1.0, (base + stability_ratio) / 2.0), 6)

    def status(self):
        unit = self.infer_as_unit()
        return {
            "samples": len(self.samples),
            "approx_as_value": unit if unit else 0.0,
            "stability_count": self.stability_count,
            "reliability_score": self.reliability()
        }


class ZTick:
    __history = []
    __max_history = 15
    __fail_count = 0
    __fail_limit = 3
    __c = 1.0
    __last_eval = "N/A"
    __ztimer = __ZIntTime()
    __arena = __ARENA()

    @staticmethod
    def __z_distilhash(t1, t2, drift):
        base = (t2 ^ t1) ^ int(drift * 1e12)
        rotated = ((base << 3) & 0xFFFFFFFFFFFFFFFF) | (base >> 61)
        hashed = (rotated * 0xA5A5A5A5A5A5A5A5) & 0xFFFFFFFFFFFFFFFF
        return hex(hashed ^ (hashed >> 32))[2:10]

    @staticmethod
    def __update_sync_ratio(expected, actual):
        ratio = actual / (expected + 1e-9)
        ZTick.__history.append(ratio)
        if len(ZTick.__history) > ZTick.__max_history:
            ZTick.__history.pop(0)
        smoothed = sum(ZTick.__history) / len(ZTick.__history)
        ZTick.__c = (ZTick.__c * 0.8) + (smoothed * 0.2)

    @staticmethod
    def __dynamic_margin():
        if len(ZTick.__history) < 4:
            return 0.001
        mean = sum(ZTick.__history) / len(ZTick.__history)
        var = sum((x - mean) ** 2 for x in ZTick.__history) / len(ZTick.__history)
        envelope = min(0.0035, 0.001 + math.sqrt(var) * 1.75)
        return envelope

    @staticmethod
    def __evaluate_behavior(drift):
        if drift < 0.0003:
            return "✔ Stable"
        elif drift < 0.001:
            return "⚠️ Minor jitter"
        else:
            return "❌ Instability"

    @staticmethod
    def wait(duration, scale="s"):
        if ZTick.__fail_count >= ZTick.__fail_limit:
            raise RuntimeError("ZTick: Temporal instability — fail-safe triggered.")

        if scale not in _SCALE_FACTORS:
            raise ValueError(f"Unsupported scale '{scale}'. Use one of: {', '.join(_SCALE_FACTORS)}")

        τ = duration * _SCALE_FACTORS[scale]
        ε = 800

        t_start = time.time_ns()
        while time.time_ns() - t_start < τ / 2:
            pass
        t_mid = time.time_ns()
        while time.time_ns() - t_start < τ:
            pass
        t_end = time.time_ns()

        actual_time = t_end - t_start
        expected_time = ZTick.__c * τ
        drift = abs((actual_time - expected_time) / (expected_time + ε))

        ZTick.__update_sync_ratio(τ, actual_time)
        margin = ZTick.__dynamic_margin()
        eval_status = ZTick.__evaluate_behavior(drift)
        ZTick.__last_eval = eval_status

        ZTick.__ztimer.update()
        ZTick.__arena.probe()

        if drift > margin:
            ZTick.__fail_count += 1
            zcode = ZTick.__z_distilhash(t_start, t_end, drift)
            raise RuntimeError(f"ZTick Drift Error: Δ={drift:.8f} > {margin:.8f} | Z-Code={zcode} | Eval={eval_status}")
        else:
            ZTick.__fail_count = 0

    @staticmethod
    def status():
        avg_drift = sum([abs(r - 1.0) for r in ZTick.__history]) / max(1, len(ZTick.__history))
        arena_status = ZTick.__arena.status()
        return {
            "sync_ratio": round(ZTick.__c, 8),
            "failures": ZTick.__fail_count,
            "avg_drift": round(avg_drift, 9),
            "history_len": len(ZTick.__history),
            "stability_margin": round(ZTick.__dynamic_margin(), 9),
            "last_eval": ZTick.__last_eval,
            "ztick_time": ZTick.__ztimer.current_time(),
            "approx_as_unit": arena_status["approx_as_value"],
            "arena_samples": arena_status["samples"],
            "arena_stability": arena_status["stability_count"],
            "arena_reliability": arena_status["reliability_score"]
        }
