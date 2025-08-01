# mlektic/reporting/utils.py
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Any

_MODEL_NAME_MAP_ES = {
    "LinearRegressionArchtImpl":   "Regresión Lineal",
    "LogisticRegressionArchtImpl": "Regresión Logística",
    "Sequential":                  "Red Neuronal Artificial",
    "TorchNNArchtImpl":            "Red Neuronal Artificial",
}
_MODEL_NAME_MAP_EN = {
    "LinearRegressionArchtImpl":   "Linear Regression",
    "LogisticRegressionArchtImpl": "Logistic Regression",
    "Sequential":                  "Artificial Neural Network",
    "TorchNNArchtImpl":            "Artificial Neural Network",
}

def nice_model_name(raw: str, language: str = "es") -> str:
    lang = (language or "es").lower()
    if lang == "en":
        return _MODEL_NAME_MAP_EN.get(raw, raw)
    return _MODEL_NAME_MAP_ES.get(raw, raw)

def fmt_datetime(dt: datetime | None) -> str:
    if dt is None:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M:%S") + f".{int(dt.microsecond/1e4):02d}"

def fmt_duration(t0: datetime | None, t1: datetime | None) -> str:
    if not (t0 and t1):
        return "N/A"
    delta: timedelta = t1 - t0
    secs = delta.total_seconds()
    if secs < 1:
        return f"{secs*1000:.0f} ms"
    if secs < 60:
        return f"{secs:.2f} s"
    m, s = divmod(secs, 60)
    if m < 60:
        return f"{int(m):02d}:{s:05.2f}"
    h, m = divmod(m, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:05.2f}"

def fmt_float(x: Any, dec: int = 4) -> str:
    try:
        val = f"{float(x):.{dec}f}"
        return f"\\({val}\\)"
    except Exception:
        return str(x)
        return str(x)