# mlektic\logistic_reg\metrics_binary.py
from __future__ import annotations
import numpy as np
import pandas as pd


def _to_numpy(x, backend: str):
    backend = (backend or "torch").lower()
    if backend == "torch":
        try:
            import torch  # type: ignore
            if isinstance(x, torch.Tensor):
                return x.detach().cpu().numpy()
        except Exception:
            pass
        return np.asarray(x)
    if backend == "tf":
        try:
            import tensorflow as tf  # type: ignore
            if isinstance(x, tf.Tensor):
                return x.numpy()
        except Exception:
            pass
        return np.asarray(x)
    return np.asarray(x)


_EPS = 1e-8


def _prep(y_true, y_prob, *, backend: str):
    """y_true → vector {0,1}; y_prob → vector prob. positiva; y_pred duro."""
    yt = _to_numpy(y_true, backend)
    yp = _to_numpy(y_prob, backend)

    if yt.ndim == 2 and yt.shape[1] == 2:  # one‑hot opcional
        yt = yt.argmax(axis=1)
    else:
        yt = yt.reshape(-1)

    yp = yp.reshape(-1)
    y_pred = (yp >= 0.5).astype(np.int32)
    y_true = yt.astype(np.int32)
    return y_true, y_pred


# ── métricas --------------------------------------------------------------
def accuracy(y_true, y_prob, *, backend: str = "torch") -> float:
    y_true, y_pred = _prep(y_true, y_prob, backend=backend)
    return float((y_true == y_pred).mean())


def precision(y_true, y_prob, *, backend: str = "torch") -> float:
    y_true, y_pred = _prep(y_true, y_prob, backend=backend)
    tp = int(((y_pred == 1) & (y_true == 1)).sum())
    fp = int(((y_pred == 1) & (y_true == 0)).sum())
    return float(tp / (tp + fp + _EPS))


def recall(y_true, y_prob, *, backend: str = "torch") -> float:
    y_true, y_pred = _prep(y_true, y_prob, backend=backend)
    tp = int(((y_pred == 1) & (y_true == 1)).sum())
    fn = int(((y_pred == 0) & (y_true == 1)).sum())
    return float(tp / (tp + fn + _EPS))


def f1_score(y_true, y_prob, *, backend: str = "torch") -> float:
    p = precision(y_true, y_prob, backend=backend)
    r = recall(y_true, y_prob, backend=backend)
    return float(2 * p * r / (p + r + _EPS))


# ── matriz de confusión (binaria) ----------------------------------------
def confusion_matrix(y_true, y_pred, *, to_df: bool = True, backend: str = "torch"):
    """
    Matriz de confusión **binaria** (enteros ≥ 0).
    y_pred puede ser prob. positiva (sigmoid) o matriz (n,2) softmax.
    """
    yp = _to_numpy(y_pred, backend)
    if yp.ndim == 2 and yp.shape[1] == 2:
        y_prob = yp[:, 1]
    else:
        y_prob = yp.reshape(-1)

    y_true_vec, y_pred_cls = _prep(y_true, y_prob, backend=backend)

    tp = int(((y_pred_cls == 1) & (y_true_vec == 1)).sum())
    fp = int(((y_pred_cls == 1) & (y_true_vec == 0)).sum())
    tn = int(((y_pred_cls == 0) & (y_true_vec == 0)).sum())
    fn = int(((y_pred_cls == 0) & (y_true_vec == 1)).sum())

    if not to_df:
        # 2×2 en numpy (el llamador puede envolver si necesita tensor)
        return np.array([[tn, fp], [fn, tp]], dtype=np.int64)

    labels  = ['Predicted Positive (1)', 'Predicted Negative (0)']
    columns = ['Actual Positive (1)',   'Actual Negative (0)']
    df = pd.DataFrame([[0, 0], [0, 0]], index=labels, columns=columns)
    df['Actual Positive (1)'] = [f"{tp} True Positives (TP)",
                                 f"{fn} False Negatives (FN)"]
    df['Actual Negative (0)'] = [f"{fp} False Positives (FP)",
                                 f"{tn} True Negatives (TN)"]
    df = df[['Actual Positive (1)', 'Actual Negative (0)']]
    return df
