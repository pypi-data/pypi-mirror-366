# mlektic/preprocessing/dataframes_utils.py
import pandas as pd
import polars as pl
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from typing import Tuple, List, Optional

# ─────────────────────────────────────────────────────────────
#  Subclase que permite colgar atributos (__dict__) a ndarray
# ─────────────────────────────────────────────────────────────
class _MetaNDArray(np.ndarray):
    """ndarray que admite atributos arbitrarios."""
    ...

# ---------- utilidades de metadatos --------------------------------
def _to_meta(arr: np.ndarray | None):        # ← acepta None
    """
    Devuelve una *vista* del array como _MetaNDArray.
    Si arr es None, lo devuelve tal cual (necesario cuando no hay val_set).
    """
    if arr is None:
        return None
    return arr if isinstance(arr, _MetaNDArray) else arr.view(_MetaNDArray)

def _attach_meta(
    Xtr, Xval, Xte,
    ytr, yval, yte,
    in_cols: List[str], out_col: str
):
    """
    Cuelga metadatos (_feature_names / _target_name) en TODOS los arrays
    que existen (ignora los que sean None) para que los modelos y el
    ReportBuilder recuperen nombres reales sin pasos extra.
    """
    Xtr, Xval, Xte = map(_to_meta, (Xtr, Xval, Xte))
    ytr, yval, yte = map(_to_meta, (ytr, yval, yte))

    for Xa in (Xtr, Xval, Xte):
        if Xa is not None:
            Xa._feature_names = list(in_cols)

    for ya in (ytr, yval, yte):
        if ya is not None:
            ya._target_name = str(out_col)

    return Xtr, Xval, Xte, ytr, yval, yte

# ─────────────────────────────────────────────────────────────
#  Funciones de split para pandas y polars
# ─────────────────────────────────────────────────────────────
def _split_dataframe(
    X: np.ndarray,
    y: np.ndarray,
    *,
    train_fraction: float,
    val_fraction: Optional[float],
    shuffle: bool,
    random_seed: int
):
    """
    Hace el split train / (val) / test manteniendo las fracciones indicadas.
    Si val_fraction es None, sólo devuelve train y test.
    """
    if val_fraction is None:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            train_size=train_fraction,
            random_state=random_seed,
            shuffle=shuffle,
        )
        return (X_train, y_train), None, (X_test, y_test)

    if train_fraction + val_fraction >= 1.0:
        raise ValueError("train_fraction + val_fraction debe ser < 1.0")

    # primero separamos train+val de test
    X_tmp, X_test, y_tmp, y_test = train_test_split(
        X, y,
        train_size=train_fraction + val_fraction,
        random_state=random_seed,
        shuffle=shuffle,
    )
    # dentro de tmp hacemos split de val
    rel_val = val_fraction / (train_fraction + val_fraction)
    X_train, X_val, y_train, y_val = train_test_split(
        X_tmp, y_tmp,
        test_size=rel_val,
        random_state=random_seed,
        shuffle=shuffle,
    )
    return (X_train, y_train), (X_val, y_val), (X_test, y_test)

# -----------------------------------------------------------------
def pd_dataset(
    df: pd.DataFrame,
    input_columns: List[str],
    output_column: str,
    train_fraction: float,
    *,
    val_fraction: Optional[float] = None,
    shuffle: bool = True,
    random_seed: int = 42,
    normalize: bool = False,
    normalization_type: str = "standard",
) -> Tuple[
    Tuple[np.ndarray, np.ndarray],
    Tuple[np.ndarray, np.ndarray],
    Tuple[np.ndarray, np.ndarray] | None,
]:
    """
    Divide un DataFrame de pandas en *train / (val) / test* devolviendo
    TUPLAS (X, y).

    • Si **val_fraction** es ``None`` (default) ⇒ retorna *(train_set, test_set)*.<br>
    • Si val_fraction es un ``float`` (por ejemplo 0.1) ⇒ retorna
      *(train_set, val_set, test_set)*.

    Los ndarrays llevan metadatos ``_feature_names`` y ``_target_name`` para que
    los modelos (lineal / logística) y el ReportBuilder muestren los nombres
    reales sin pasos extra.

    Parameters
    ----------
    df : pd.DataFrame
        Conjunto de datos completo.
    input_columns : list[str]
        Columnas de entrada (features) a usar.
    output_column : str
        Columna objetivo (target).
    train_fraction : float
        Proporción de datos destinados a entrenamiento.
    val_fraction : float | None, default None
        Fracción del total para validación (dev).  Si es ``None`` no se crea
        conjunto de validación.
    shuffle, random_seed
        Se pasan directamente a ``train_test_split``.
    normalize : bool, default False
        Si ``True`` normaliza **sólo** las *features* con standard / min-max.
    normalization_type : {"standard","minmax"}, default "standard"
        Algoritmo de normalización cuando *normalize=True*.

    Returns
    -------
    • Sin ``val_fraction`` ⇒ *(train_set, test_set)*  
    • Con ``val_fraction`` ⇒ *(train_set, val_set, test_set)*
    """
    X = df[input_columns].to_numpy()
    y = df[output_column].to_numpy()

    if normalize:
        scaler = StandardScaler() if normalization_type == "standard" else MinMaxScaler()
        X = scaler.fit_transform(X)

    train_set, val_set, test_set = _split_dataframe(
        X, y,
        train_fraction=train_fraction,
        val_fraction=val_fraction,
        shuffle=shuffle,
        random_seed=random_seed,
    )

    # Metadatos ------------------------
    if val_set is None:
        (Xtr, ytr), (Xte, yte) = train_set, test_set
        Xtr, Xval, Xte, ytr, yval, yte = _attach_meta(
            Xtr, None, Xte, ytr, None, yte, input_columns, output_column
        )
        return (Xtr, ytr), (Xte, yte)
    else:
        (Xtr, ytr), (Xval, yval), (Xte, yte) = train_set, val_set, test_set
        Xtr, Xval, Xte, ytr, yval, yte = _attach_meta(
            Xtr, Xval, Xte, ytr, yval, yte, input_columns, output_column
        )
        return (Xtr, ytr), (Xval, yval), (Xte, yte)

# -----------------------------------------------------------------
def pl_dataset(
    df: pl.DataFrame,
    input_columns: List[str],
    output_column: str,
    train_fraction: float,
    *,
    val_fraction: Optional[float] = None,
    shuffle: bool = True,
    random_seed: int = 42,
    normalize: bool = False,
    normalization_type: str = "standard",
) -> Tuple[
    Tuple[np.ndarray, np.ndarray],
    Tuple[np.ndarray, np.ndarray],
    Tuple[np.ndarray, np.ndarray] | None,
]:
    """
    Igual que `pd_dataset`, pero acepta `polars.DataFrame`.
    """
    X = df.select(input_columns).to_numpy()
    y = df.select(output_column).to_numpy().flatten()

    if normalize:
        scaler = StandardScaler() if normalization_type == "standard" else MinMaxScaler()
        X = scaler.fit_transform(X)

    train_set, val_set, test_set = _split_dataframe(
        X, y,
        train_fraction=train_fraction,
        val_fraction=val_fraction,
        shuffle=shuffle,
        random_seed=random_seed,
    )

    # Metadatos ------------------------
    if val_set is None:
        (Xtr, ytr), (Xte, yte) = train_set, test_set
        Xtr, Xval, Xte, ytr, yval, yte = _attach_meta(
            Xtr, None, Xte, ytr, None, yte, input_columns, output_column
        )
        return (Xtr, ytr), (Xte, yte)
    else:
        (Xtr, ytr), (Xval, yval), (Xte, yte) = train_set, val_set, test_set
        Xtr, Xval, Xte, ytr, yval, yte = _attach_meta(
            Xtr, Xval, Xte, ytr, yval, yte, input_columns, output_column
        )
        return (Xtr, ytr), (Xval, yval), (Xte, yte)
