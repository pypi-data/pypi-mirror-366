#mlektic\logistic_reg\logistic_regression_archt.py
from __future__ import annotations
import importlib, json
from pathlib import Path

_BACKENDS = {
    "torch": "mlektic.logistic_reg.logistic_regression_torch",
    "tf":    "mlektic.logistic_reg.logistic_regression_tf",   # ← el módulo ya existente
}

def _load_cls(backend: str):
    mod = importlib.import_module(_BACKENDS[backend])
    return mod.LogisticRegressionArchtImpl                 # cada backend expone esto

def LogisticRegressionArcht(*args, backend: str = "torch", **kwargs):
    cls = _load_cls(backend.lower())
    return cls(*args, **kwargs)

# ── snapshot loader (backend autodetect) ─────────────────────────────────
def _from_file(filepath: str, *, backend: str | None = None):
    payload = json.load(open(filepath, "r", encoding="utf‑8"))
    bk = (payload.get("config", {}).get("backend") or backend or "torch").lower()
    cls = _load_cls(bk)
    return cls.from_file(filepath)

setattr(LogisticRegressionArcht, "from_file", staticmethod(_from_file))
