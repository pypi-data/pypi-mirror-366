# mlektic/linear_reg/linreg_utils.py
"""
Métricas basadas en TensorFlow (opcional).

El módulo se carga aunque TensorFlow no exista.  Si alguna función se llama
sin tener TF instalado, se lanza un ImportError descriptivo.
"""
from __future__ import annotations
import importlib

_tf_spec = importlib.util.find_spec("tensorflow")
if _tf_spec is not None:
    import tensorflow as tf

    def _as_tf(x):
        return tf.convert_to_tensor(x, dtype=tf.float32)

    def calculate_mse(y_true, y_pred):
        y_true = _as_tf(y_true); y_pred = _as_tf(y_pred)
        return tf.reduce_mean(tf.square(y_pred - y_true))

    def calculate_rmse(y_true, y_pred):
        return tf.sqrt(calculate_mse(y_true, y_pred))

    def calculate_mae(y_true, y_pred):
        y_true = _as_tf(y_true); y_pred = _as_tf(y_pred)
        return tf.reduce_mean(tf.abs(y_pred - y_true))

    def calculate_mape(y_true, y_pred):
        y_true = _as_tf(y_true); y_pred = _as_tf(y_pred)
        return tf.reduce_mean(tf.abs((y_true - y_pred) / y_true)) * 100.0

    def calculate_r2(y_true, y_pred):
        y_true = _as_tf(y_true); y_pred = _as_tf(y_pred)
        ss_res = tf.reduce_sum(tf.square(y_true - y_pred))
        ss_tot = tf.reduce_sum(tf.square(y_true - tf.reduce_mean(y_true)))
        return 1.0 - ss_res / ss_tot

    def calculate_pearson_correlation(y_true, y_pred):
        y_true = _as_tf(y_true); y_pred = _as_tf(y_pred)
        y_true -= tf.reduce_mean(y_true)
        y_pred -= tf.reduce_mean(y_pred)
        numerator   = tf.reduce_sum(y_true * y_pred)
        denominator = tf.sqrt(tf.reduce_sum(tf.square(y_true)) *
                              tf.reduce_sum(tf.square(y_pred)))
        return numerator / denominator
else:
    # TensorFlow no está: definir wrappers que avisen claramente.
    _MSG = (
        "Esta función requiere TensorFlow. "
        "Instálalo con `pip install tensorflow` para usarla."
    )

    def _no_tf(*_, **__):
        raise ImportError(_MSG)

    calculate_mse = calculate_rmse = calculate_mae = calculate_mape = \
        calculate_r2 = calculate_pearson_correlation = _no_tf
