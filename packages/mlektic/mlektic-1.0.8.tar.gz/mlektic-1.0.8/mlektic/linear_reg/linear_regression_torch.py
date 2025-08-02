# mlektic/linear_reg/linear_regression_torch.py
import json, numpy as np, torch
from pathlib import Path
from collections import deque
from typing import Optional, Tuple, Dict, Any
from ..methods.linreg_trainers_torch import build_trainer
from .linreg_utils_torch import (mse, rmse, mae, mape, r2, corr)
from collections import deque
from datetime import datetime as _dt

_VALID_METRICS = {"mse","rmse","mae","mape","r2","corr"}
_VALID_INITS = {
    "zeros":        lambda s: torch.zeros(s, dtype=torch.float32),
    "random_normal":lambda s: torch.randn(s, dtype=torch.float32)*1e-2,
    "glorot":       lambda s: torch.randn(s, dtype=torch.float32)*np.sqrt(2/sum(s)),
}

class _EarlyStopper:
    def __init__(self, *, patience: int, min_delta: float):
        self.patience = patience
        self.min_delta = min_delta
        self.best_loss = float("inf")
        self._wait = 0

    def __call__(self, loss: float) -> bool:
        if self.best_loss - loss > self.min_delta:
            self.best_loss = loss
            self._wait = 0
        else:
            self._wait += 1
        return self._wait >= self.patience

def _standardize(X, mean, std): return (X-mean)/std

class LinearRegressionArchtImpl:
    def __init__(
        self,
        *, iterations:int=50, use_intercept:bool=True, verbose:bool=True,
        regularizer:Optional[Any]=None, optimizer:Optional[Any]=None,
        method:str="least_squares", metric:str="mse", tol:float=1e-6,
        weight_init:str="zeros", random_state:int|None=None,
        early_stopping:Optional[Dict[str,Any]]=None, standardize:bool=False,
    ):
        # reproducibilidad
        if random_state is not None:
            torch.manual_seed(random_state)
            np.random.seed(random_state)

        # hiper‑parámetros
        self.iterations, self.use_intercept, self.verbose = iterations, use_intercept, verbose
        self.regularizer, self.method = regularizer, method.lower()
        self.metric, self.tol = metric.lower(), tol
        self.weight_init, self.standardize = weight_init, standardize
        self.batch_size = None

        # ── históricos ----------------------------------------------------
        self.cost_history   = deque()
        self.metric_history = deque()
        setattr(self, f"{self.metric}_history", deque())

        # runtime
        self.cost_history   = deque()
        self.metric_history = deque()
        self.weights        = None
        self.n_features     = None
        self.feature_mean_  = None
        self.feature_std_   = None

        # snapshots / early stop
        self._snapshots       = {}
        self._early_stop_epoch= None

        # optimizador
        if optimizer is None:
            self._make_optimizer = lambda p: torch.optim.SGD(p, lr=1e-2)
        elif callable(optimizer):
            self._make_optimizer = optimizer
        elif isinstance(optimizer, (tuple, list)):
            if callable(optimizer[0]):
                self._make_optimizer = optimizer[0]
                if len(optimizer) > 1 and isinstance(optimizer[1], str):
                    self.method = optimizer[1].lower()
                if len(optimizer) == 3:
                    self.batch_size = optimizer[2]
            elif isinstance(optimizer[0], str):
                name, lr = optimizer[:2]
                self._make_optimizer = lambda p: getattr(torch.optim, name.upper())(p, lr)
            else:
                raise ValueError("Formato de 'optimizer' no reconocido.")
        else:
            raise TypeError("'optimizer' debe ser None, callable o tuple/list.")

        # early‑stopping
        self._early = _EarlyStopper(**early_stopping) if early_stopping else None

        if metric not in _VALID_METRICS:
            raise ValueError(f"Métrica '{metric}' no soportada: {_VALID_METRICS}")

    # --- helpers ----------------------------------------------------
    def _metric_fn(self):
        return dict(mse=mse, rmse=rmse, mae=mae, mape=mape, r2=r2, corr=corr)[self.metric]

    def _predict(self,X): return X @ self.weights

    def _loss(self,X,y):
        pred = self._predict(X)
        loss = mse(y,pred)
        if self.regularizer: loss += self.regularizer(self.weights)
        return loss

    def _init_weights(self):
        init = _VALID_INITS[self.weight_init]
        self.weights = torch.nn.Parameter(init((self.n_features,1)))
        self.opt = self._make_optimizer([self.weights])
        self.optimizer = self.opt  

    # --- training ---------------------------------------------------------
    def train(
        self,
        train_set: Tuple[np.ndarray, np.ndarray],
        *,
        val_set: Optional[Tuple[np.ndarray, np.ndarray]] = None,
        test_set: Optional[Tuple[np.ndarray, np.ndarray]] = None,
    ):
        """
        Entrena la regresión lineal y, además, captura:
        • feature_names (si X es DataFrame o array con dtype.names)
        • target_name   (si y es Series con .name)
        para que el ReportBuilder los recupere sin pasos extra.
        """
        self._mlektic_t0 = _dt.now()
        try:
            X_np, y_np = train_set

            # Registrar sets para el reporte
            self._mlektic_X_train = X_np
            self._mlektic_y_train = y_np
            if val_set is not None:
                self._mlektic_X_val,  self._mlektic_y_val  = val_set
            if test_set is not None:
                self._mlektic_X_test, self._mlektic_y_test = test_set

            # -------- nombres: features / target --------------------------------
            feat_names = None
            try:
                if hasattr(X_np, "columns"):                         # pandas.DataFrame
                    feat_names = list(getattr(X_np, "columns"))
                elif isinstance(X_np, np.ndarray) and getattr(X_np.dtype, "names", None):
                    feat_names = list(X_np.dtype.names)              # ndarray estructurado
                elif hasattr(X_np, "_feature_names"):
                    feat_names = list(getattr(X_np, "_feature_names"))  # compat. antiguo
            except Exception:
                pass

            tname = None
            try:
                if hasattr(y_np, "name") and getattr(y_np, "name") is not None:
                    tname = str(getattr(y_np, "name"))
                elif hasattr(y_np, "_target_name"):
                    tname = str(getattr(y_np, "_target_name"))
            except Exception:
                pass
            self._target_name = tname or "y"

            # -------- tensores ---------------------------------------------------
            # ⚠️ Usar np.float32 (NumPy), no torch.float32
            X_arr = np.asarray(X_np, dtype=np.float32)
            y_arr = np.asarray(y_np, dtype=np.float32).reshape(-1, 1)

            X = torch.tensor(X_arr, dtype=torch.float32)
            y = torch.tensor(y_arr, dtype=torch.float32)

            # estandarización
            if self.standardize:
                self.feature_mean_ = X.mean(0, keepdim=True)
                self.feature_std_  = X.std(0, keepdim=True) + 1e-8
                X = _standardize(X, self.feature_mean_, self.feature_std_)

            # intercepto
            if self.use_intercept:
                X = torch.cat([torch.ones(len(X), 1), X], 1)
            self.n_features = X.shape[1]

            # nombres de features (longitud coherente)
            n_no_bias = self.n_features - int(self.use_intercept)
            if not feat_names or len(feat_names) != n_no_bias:
                feat_names = [f"x{i+1}" for i in range(n_no_bias)]
            self.feature_names  = feat_names
            self._feature_names = feat_names

            # ---------- solución analítica (least squares) -----------------------
            if self.method == "least_squares":
                XtX = X.T @ X
                Xty = X.T @ y
                self.weights = torch.linalg.solve(XtX, Xty)
                self.cost_history.append(float(mse(y, self._predict(X))))
                return self

            # ---------- métodos basados en gradiente ----------------------------
            self._init_weights()
            hist_name = f"{self.metric}_history"

            trainer = build_trainer(
                method        = self.method,
                model         = self,
                optimizer     = self.opt,
                iterations    = self.iterations,
                batch_size    = self.batch_size,
                tol           = self.tol,
                early_stopper = self._early,
            )

            # Hook para capturar métricas por época
            def after_epoch(loss_val):
                metric_val = float(self._metric_fn()(y, self._predict(X)))
                self.metric_history.append(metric_val)
                getattr(self, hist_name).append(metric_val)

            trainer.after_epoch = after_epoch
            trainer.run(X, y)
            return self
        finally:
            self._mlektic_t1 = _dt.now()

    # --- predict / eval --------------------------------------------
    def _prep(self, x):
        # ➋ aceptar diccionarios
        if isinstance(x, dict):
            if not hasattr(self, "feature_names"):
                raise ValueError(
                    "El modelo no dispone de 'feature_names'; "
                    "pasa una lista/array en su lugar."
                )
            x = torch.tensor(
                [x[n] for n in self.feature_names], dtype=torch.float32
            )

        elif isinstance(x, (list, tuple)):
            x = torch.tensor(x, dtype=torch.float32)
        elif isinstance(x, np.ndarray):
            x = torch.tensor(x, dtype=torch.float32)
        elif isinstance(x, float):
            x = torch.tensor([x], dtype=torch.float32)
        else:
            raise TypeError("Formato de entrada no soportado.")

        if x.ndim == 1:
            x = x.unsqueeze(0)

        if self.standardize:
            x = _standardize(x, self.feature_mean_, self.feature_std_)
        if self.use_intercept:
            x = torch.cat([torch.ones(len(x), 1), x], 1)
        return x
    
    def predict(self,x): return self._predict(self._prep(x)).detach().numpy()

    def eval(self, test_set, metric=None, *, role: str = "test"):
        """
        Evalúa y registra el conjunto como 'test' (por defecto) o 'val'
        para que el ReportBuilder conozca el split real.
        """
        metric = metric or self.metric
        X_np, y_np = test_set
        if role == "val":
            self._mlektic_X_val,  self._mlektic_y_val  = X_np, y_np
        else:
            self._mlektic_X_test, self._mlektic_y_test = X_np, y_np

        # → Conversión consistente a float32 de NumPy
        X_arr = np.asarray(X_np, dtype=np.float32)
        y_arr = np.asarray(y_np, dtype=np.float32).reshape(-1, 1)

        X = torch.tensor(X_arr, dtype=torch.float32)
        y = torch.tensor(y_arr, dtype=torch.float32)

        if self.standardize:
            X = _standardize(X, self.feature_mean_, self.feature_std_)
        if self.use_intercept:
            X = torch.cat([torch.ones(len(X), 1), X], 1)

        fn = dict(mse=mse, rmse=rmse, mae=mae, mape=mape, r2=r2, corr=corr)[metric]
        return float(fn(y.view(-1, 1), self._predict(X)).item())
    
    def get_cost_history(self, *, as_list: bool = True):
        """
        Devuelve la traza de costes registrada durante el entrenamiento.

        Parameters
        ----------
        as_list : bool, default True
            • True  → convierte el deque interno a una lista «normal».
            • False → devuelve directamente el deque para quien
              necesite mutabilidad o máxima eficiencia.

        Returns
        -------
        list | collections.deque
            La secuencia de valores de pérdida epoch‑a‑epoch.
        """
        return list(self.cost_history) if as_list else self.cost_history     

    # --------------------- parámetros e intercepto ---------------------
    def get_parameters(self) -> np.ndarray:
        """
        Devuelve los pesos (sin el sesgo) en forma de ``ndarray``.

        Raises
        ------
        RuntimeError
            Si el modelo aún no ha sido entrenado.
        """
        if self.weights is None:
            raise RuntimeError("Call train() before accessing the parameters.")
        if self.use_intercept:
            return self.weights[1:].detach().numpy()
        return self.weights.detach().numpy()

    def get_intercept(self) -> Optional[float]:
        """
        Devuelve el término de sesgo (bias) o ``None`` si se desactivó.

        Raises
        ------
        RuntimeError
            Si el modelo aún no ha sido entrenado.
        """
        if not self.use_intercept:
            return None
        if self.weights is None:
            raise RuntimeError("Call train() before accessing the intercept.")
        return float(self.weights[0].detach().item())       

    # --- (de)serialisation -----------------------------------------
    def save_model(self, fname):
        data = dict(
            config=dict(
                use_intercept = self.use_intercept,
                standardize   = self.standardize,
                n_features    = self.n_features,
            ),
            weights       = self.weights.detach().numpy().tolist(),
            cost_history  = list(self.cost_history),

            # ⬇ NUEVO: medias / std (o None si no hay escalado)
            feature_mean_ = (
                None if self.feature_mean_ is None
                else self.feature_mean_.detach().numpy().tolist()
            ),
            feature_std_  = (
                None if self.feature_std_ is None
                else self.feature_std_.detach().numpy().tolist()
            ),
        )
        Path(fname).parent.mkdir(parents=True, exist_ok=True)
        json.dump(data, open(fname, "w"))

    # ── from_file() ───────────────────────────────────────────────
    @classmethod
    def from_file(cls, fname):
        payload = json.load(open(fname))
        cfg = payload["config"]

        mdl = cls(
            use_intercept = cfg["use_intercept"],
            standardize   = cfg["standardize"],
        )
        mdl.n_features = cfg["n_features"]
        mdl._init_weights()
        mdl.weights.data = torch.tensor(payload["weights"], dtype=torch.float32)
        mdl.cost_history = deque(payload["cost_history"])

        # ⬇ NUEVO: restaurar escalador, si existe
        if payload.get("feature_mean_") is not None:
            mdl.feature_mean_ = torch.tensor(payload["feature_mean_"],
                                            dtype=torch.float32)
        if payload.get("feature_std_") is not None:
            mdl.feature_std_  = torch.tensor(payload["feature_std_"],
                                            dtype=torch.float32)

        # nombres de features para predicción con dict
        mdl.feature_names = [
            f"x{i+1}" for i in range(mdl.n_features - int(mdl.use_intercept))
        ]
        return mdl

