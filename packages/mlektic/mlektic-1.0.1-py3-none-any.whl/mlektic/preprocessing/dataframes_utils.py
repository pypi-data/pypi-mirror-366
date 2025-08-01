# mlektic/preprocessing/dataframes_utils.py
import pandas as pd
import polars as pl
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from typing import Tuple, List

# ─────────────────────────────────────────────────────────────
# Pequeña subclase para poder colgar atributos en los ndarray
# ─────────────────────────────────────────────────────────────
class _MetaNDArray(np.ndarray):
    """ndarray que permite atributos arbitrarios (_feature_names, _target_name, etc.)."""
    pass


def _to_meta(arr: np.ndarray) -> _MetaNDArray:
    """Devuelve una vista del array como _MetaNDArray (idempotente)."""
    if isinstance(arr, _MetaNDArray):
        return arr
    # view no copia datos
    return arr.view(_MetaNDArray)


def _attach_meta(Xtr, Xte, ytr, yte, in_cols, out_col):
    """
    Cuelga metadatos en los arrays para que el ReportBuilder/collector
    puedan recuperarlos sin que el usuario tenga que pasarlos a mano.
    """
    Xtr = _to_meta(Xtr);  Xte = _to_meta(Xte)
    ytr = _to_meta(ytr);  yte = _to_meta(yte)

    # Estos atributos los buscará el builder/collector
    Xtr._feature_names = list(in_cols)
    Xte._feature_names = list(in_cols)
    ytr._target_name   = str(out_col)
    yte._target_name   = str(out_col)

    return Xtr, Xte, ytr, yte
# ─────────────────────────────────────────────────────────────

def pd_dataset(
    df: pd.DataFrame,
    input_columns: List[str],
    output_column: str,
    train_fraction: float,
    shuffle: bool = True,
    random_seed: int = 42,
    normalize: bool = False,
    normalization_type: str = 'standard'
) -> Tuple[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]:
    """
    Divide un DataFrame de pandas en train/test y devuelve tuplas (X, y).

    Nota: ya NO se cuelgan metadatos (_feature_names/_target_name) en los
    ndarrays devueltos. Los nombres se capturan en `train()` del modelo si
    pasas directamente DataFrames/Series a ese método.
    """
    X = df[input_columns].values
    y = df[output_column].values

    if normalize:
        if normalization_type == 'standard':
            scaler = StandardScaler()
        elif normalization_type == 'minmax':
            scaler = MinMaxScaler()
        else:
            raise ValueError("Unsupported normalization_type. Choose 'standard' or 'minmax'.")
        X = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, train_size=train_fraction, random_state=random_seed, shuffle=shuffle
    )
    return (X_train, y_train), (X_test, y_test)


def pl_dataset(
    df: pl.DataFrame,
    input_columns: List[str],
    output_column: str,
    train_fraction: float,
    shuffle: bool = True,
    random_seed: int = 42,
    normalize: bool = False,
    normalization_type: str = 'standard'
) -> Tuple[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]:
    """
    Versión para Polars. Igual que pd_dataset, ya SIN metadatos adjuntos.
    """
    X = df.select(input_columns).to_numpy()
    y = df.select(output_column).to_numpy().flatten()

    if normalize:
        if normalization_type == 'standard':
            scaler = StandardScaler()
        elif normalization_type == 'minmax':
            scaler = MinMaxScaler()
        else:
            raise ValueError("Unsupported normalization_type. Choose 'standard' or 'minmax'.")
        X = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, train_size=train_fraction, random_state=random_seed, shuffle=shuffle
    )
    return (X_train, y_train), (X_test, y_test)
