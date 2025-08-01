# mlektic/linear_reg/linear_regression_archt.py
from __future__ import annotations
import importlib
import json
from pathlib import Path

_BACKENDS = {
    "torch": "mlektic.linear_reg.linear_regression_torch",
    "tf":    "mlektic.linear_reg.linear_regression_tf",
}

def _load_cls(backend: str):
    mod = importlib.import_module(_BACKENDS[backend])
    return mod.LinearRegressionArchtImpl       

def LinearRegressionArcht(*args, backend: str = "torch", **kwargs):
    cls = _load_cls(backend.lower())
    return cls(*args, **kwargs)

def _from_file(filepath: str, *, backend: str | None = None):
    with open(filepath, "r", encoding="utf‑8") as f:
        payload = json.load(f)
    bk = (payload.get("config", {}).get("backend") or backend or "torch").lower()
    cls = _load_cls(bk)
    return cls.from_file(filepath)

setattr(LinearRegressionArcht, "from_file", staticmethod(_from_file))
