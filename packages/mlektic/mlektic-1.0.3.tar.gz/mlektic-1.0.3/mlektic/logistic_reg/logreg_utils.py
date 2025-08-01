#mlektic\logistic_reg\logreg_utils.py
import numpy as np
import pandas as pd


def _to_numpy(x, backend: str):
    """
    Convierte x → numpy según el backend indicado.
    No fuerza la importación del otro framework.
    """
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

    # fallback puro numpy
    return np.asarray(x)


def _wrap_like_backend(arr: np.ndarray, *, backend: str, dtype_int: bool = False):
    """
    Envuelve un array numpy como tensor del backend indicado.
    Si backend no es reconocido, devuelve el numpy tal cual.
    """
    backend = (backend or "torch").lower()
    if backend == "torch":
        try:
            import torch  # type: ignore
            dt = torch.int64 if dtype_int else torch.float32
            return torch.tensor(arr, dtype=dt)
        except Exception:
            return arr
    if backend == "tf":
        try:
            import tensorflow as tf  # type: ignore
            dt = tf.int64 if dtype_int else tf.float32
            return tf.convert_to_tensor(arr, dtype=dt)
        except Exception:
            return arr
    return arr


# ───────────────────────────────────────────────
#  Pérdidas y métricas multiclase (agnósticas; usan numpy)
# ───────────────────────────────────────────────
def calculate_binary_crossentropy(y_true, y_pred, *, backend: str = "torch"):
    """
    BCE elemento a elemento entre etiquetas binarias y prob. de clase positiva.
    Soporta:
      • y_pred (n,2) → usa la col 1 (prob. positiva)
      • y_pred (n,1) o (n,) → ya es prob. positiva
    Devuelve un vector numpy de longitud n.
    """
    yp = _to_numpy(y_pred, backend)
    yt = _to_numpy(y_true, backend).reshape(-1)
    if yp.ndim == 2 and yp.shape[1] == 2:
        p = yp[:, 1]
    else:
        p = yp.reshape(-1)
    eps = 1e-8
    p = np.clip(p, eps, 1 - eps)
    return -(yt * np.log(p) + (1 - yt) * np.log(1 - p))


def calculate_categorical_crossentropy(y_true, y_pred, *, backend: str = "torch"):
    """CCE elemento a elemento para etiquetas one‑hot y probs por clase (vector numpy)."""
    yt = _to_numpy(y_true, backend)
    yp = _to_numpy(y_pred, backend)
    eps = 1e-8
    yp = np.clip(yp, eps, 1 - eps)
    return -(yt * np.log(yp)).sum(axis=1)


def calculate_accuracy(y_true, y_pred, *, backend: str = "torch"):
    """Exactitud para one‑hot y probs (float)."""
    yt = _to_numpy(y_true, backend)
    yp = _to_numpy(y_pred, backend)
    pred = yp.argmax(axis=1)
    true = yt.argmax(axis=1)
    return float((pred == true).mean())


def calculate_precision(y_true, y_pred, *, backend: str = "torch"):
    """Precisión macro‑promedio multiclase (float)."""
    yt = _to_numpy(y_true, backend); yp = _to_numpy(y_pred, backend)
    pred = yp.argmax(axis=1);        true = yt.argmax(axis=1)
    k = int(true.max()) + 1; eps = 1e-8
    vals = []
    for c in range(k):
        tp = ((pred == c) & (true == c)).sum()
        fp = ((pred == c) & (true != c)).sum()
        vals.append(tp / (tp + fp + eps))
    return float(np.mean(vals))


def calculate_recall(y_true, y_pred, *, backend: str = "torch"):
    """Recall macro‑promedio multiclase (float)."""
    yt = _to_numpy(y_true, backend); yp = _to_numpy(y_pred, backend)
    pred = yp.argmax(axis=1);        true = yt.argmax(axis=1)
    k = int(true.max()) + 1; eps = 1e-8
    vals = []
    for c in range(k):
        tp = ((pred == c) & (true == c)).sum()
        fn = ((pred != c) & (true == c)).sum()
        vals.append(tp / (tp + fn + eps))
    return float(np.mean(vals))


def calculate_f1_score(y_true, y_pred, *, backend: str = "torch"):
    """F1 macro‑promedio (float)."""
    p = calculate_precision(y_true, y_pred, backend=backend)
    r = calculate_recall(y_true, y_pred, backend=backend)
    eps = 1e-8
    return float(2 * p * r / (p + r + eps))


# ───────────────────────────────────────────────
#  Matriz de confusión (binario y multiclase) — enteros, sin negativos
# ───────────────────────────────────────────────
def calculate_confusion_matrix(
    y_true,
    y_pred,
    *,
    to_df: bool = True,
    backend: str = "torch",
    class_names: list[str] | None = None,
):
    """
    Matriz de confusión con conteos enteros (≥ 0).

    • y_true: one‑hot (n,k) o vector de clases (n,)
    • y_pred: probs (n,k)   o vector de clases (n,)   o prob. positiva (n,)
    • to_df:  True→DataFrame; False→tensor/ndarray k×k según backend.
    • class_names (opcional): nombres para columnas/filas en multiclase.

    Convención de salida:
      – Binario (DataFrame): filas=Predicción, columnas=Real (TP/FP/FN/TN como texto).
      – Multiclase: filas=Predicción, columnas=Real (k×k).
    """
    yt = _to_numpy(y_true, backend)
    yp = _to_numpy(y_pred, backend)

    # Coerción a vectores de clase
    if yt.ndim == 2:
        true_cls = yt.argmax(axis=1).astype(np.int64)
    else:
        true_cls = yt.astype(np.int64).reshape(-1)

    if yp.ndim == 2:
        pred_cls = yp.argmax(axis=1).astype(np.int64)
    else:
        pred_cls = (yp.reshape(-1) >= 0.5).astype(np.int64)

    k = int(max(true_cls.max(), pred_cls.max())) + 1

    # cm (Real x Pred) con bincount → enteros
    idx = true_cls * k + pred_cls
    cm = np.bincount(idx, minlength=k * k).reshape(k, k).astype(np.int64)

    if not to_df:
        # Devolver tensor del backend indicado
        return _wrap_like_backend(cm, backend=backend, dtype_int=True)

    if k == 2:
        tp = int(cm[1, 1]); fp = int(cm[0, 1]); tn = int(cm[0, 0]); fn = int(cm[1, 0])
        labels  = ['Predicted Positive (1)', 'Predicted Negative (0)']
        columns = ['Actual Positive (1)',   'Actual Negative (0)']
        df = pd.DataFrame([[0, 0], [0, 0]], index=labels, columns=columns)
        df['Actual Positive (1)'] = [f"{tp} True Positives (TP)", f"{fn} False Negatives (FN)"]
        df['Actual Negative (0)'] = [f"{fp} False Positives (FP)", f"{tn} True Negatives (TN)"]
        df = df[['Actual Positive (1)', 'Actual Negative (0)']]
        return df

    # Multiclase → filas=Predicción, columnas=Real (trasponer)
    cm_pred_rows = cm.T
    idx_labels = class_names if (class_names and len(class_names) == k) else [f"Predicted {c}" for c in range(k)]
    col_labels = class_names if (class_names and len(class_names) == k) else [f"Actual {c}" for c in range(k)]
    return pd.DataFrame(cm_pred_rows, index=idx_labels, columns=col_labels)
