from .linear_regression_archt import LinearRegressionArcht
from .linreg_utils import calculate_mse, calculate_mae, calculate_mape, calculate_pearson_correlation, calculate_r2, calculate_rmse
from importlib import import_module
from importlib.util import find_spec

# --- métricas ------------------------------------------------------
_has_tf = find_spec("tensorflow") is not None
if _has_tf:
    _utils = import_module(".linreg_utils", __package__)
    calculate_mse   = _utils.calculate_mse
    calculate_mae   = _utils.calculate_mae
    calculate_mape  = _utils.calculate_mape
    calculate_r2    = _utils.calculate_r2
    calculate_rmse  = _utils.calculate_rmse
    calculate_pearson_correlation = _utils.calculate_pearson_correlation
else:
    # Place-holders que lanzan un error claro si se usan sin TF.
    def _no_tf(*_, **__):
        raise ImportError(
            "Estas funciones de métrica requieren TensorFlow; "
            "instálalo con `pip install tensorflow`."
        )
    calculate_mse = calculate_mae = calculate_mape = calculate_r2 = \
        calculate_rmse = calculate_pearson_correlation = _no_tf

__all__ = [
    "LinearRegressionArcht",
    "calculate_mse", "calculate_mae", "calculate_mape",
    "calculate_r2",  "calculate_rmse", "calculate_pearson_correlation",
]