#mlektic\logistic_reg\logistic_regression_torch.py
from __future__ import annotations
import json, numpy as np, torch
from pathlib import Path
from collections import deque
from typing import Any, Callable, Dict, Optional, Tuple, Union
import torch
from ..methods.logreg_trainers_torch import build_trainer as build_torch_trainer
from collections import deque
from datetime import datetime as _dt

# ──────────── helpers & constantes ────────────
def _bce(y, p):
    eps = 1e-8;  p = torch.clamp(p, eps, 1 - eps)
    return -(y * torch.log(p) + (1 - y) * torch.log(1 - p)).mean()

def _ce(yh, ps):
    eps = 1e-8;  ps = torch.clamp(ps, eps, 1 - eps)
    return -(yh * torch.log(ps)).sum(1).mean()

def _acc_bin(y, p):  return ((p >= .5) == y).float().mean()
def _acc_mc (yh, ps): return (ps.argmax(1) == yh.argmax(1)).float().mean()

_VALID_INITS: Dict[str, Callable[[Tuple[int, ...]], torch.Tensor]] = {
    "zeros":         lambda s: torch.zeros(s, dtype=torch.float32),
    "random_normal": lambda s: torch.randn(s, dtype=torch.float32) * 1e-2,
    "glorot":        lambda s: torch.randn(s, dtype=torch.float32) * np.sqrt(2.0 / sum(s)),
}
_VALID_METRICS = {
    "accuracy", "precision", "recall", "f1_score",
    "confusion_matrix",
    "binary_crossentropy",
}

class _EarlyStopper:
    def __init__(self, *, patience:int, min_delta:float):
        self.patience, self.min_delta = patience, min_delta
        self.best, self.wait = float("inf"), 0
    def __call__(self, loss:float)->bool:
        if self.best - loss > self.min_delta:
            self.best, self.wait = loss, 0
        else: self.wait += 1
        return self.wait >= self.patience

def _standardize(X,m,s): return (X-m)/s
_EPS = 1e-8

# ──────────────── main class ────────────────
class LogisticRegressionArchtImpl:
    """
    Logistic / Soft‑max regression backend (PyTorch).
    Soporta binario (sigmoid) y multiclase (soft‑max) con:
      • batch / stochastic / mini‑batch / mle / lbfgs
      • precision / recall / f1 (macro) para multiclase
    """

    def __init__(
        self, *, iterations:int=50, use_intercept:bool=True, verbose:bool=True,
        regularizer:Optional[Callable[[torch.Tensor],torch.Tensor]]=None,
        optimizer:Optional[Any]=None,          # None | callable | (name, lr)
        method:str="mle", metric:str="accuracy", tol:float=1e-6,
        weight_init:str="zeros", random_state:Optional[int]=None,
        early_stopping:Optional[Dict[str,Any]]=None, standardize:bool=False,
        ovr:bool=False
    ):
        # ── reproducibilidad ───────────────────────────────────────
        if random_state is not None:
            torch.manual_seed(random_state)
            np.random.seed(random_state)

        # ── hiper‑parámetros principales ───────────────────────────
        self.iterations, self.use_intercept, self.verbose = iterations, use_intercept, verbose
        self.regularizer, self.method = regularizer, method.lower()
        self.metric, self.tol = metric.lower(), tol
        self.weight_init, self.standardize = weight_init, standardize
        self.ovr = ovr
        if self.metric not in _VALID_METRICS:
            raise ValueError(f"metric '{metric}' not in {_VALID_METRICS}")

        # ── históricos de entrenamiento ─────────────────────────────
        self.cost_history   = deque()            # pérdida
        self.metric_history = deque()            # alias genérico
        setattr(self, f"{self.metric}_history", deque())   # histórico específico

        # ── optimizador (idéntico al original) ─────────────────────
        self.batch_size = None
        if optimizer is None:
            self._make_opt = (
                (lambda p: torch.optim.LBFGS(p, lr=1.0, max_iter=20,
                                            line_search_fn='strong_wolfe'))
                if self.method == "lbfgs"
                else (lambda p: torch.optim.SGD(p, lr=1e-2))
            )
        elif callable(optimizer):
            self._make_opt = optimizer
        elif isinstance(optimizer, (tuple, list)):
            if callable(optimizer[0]):
                self._make_opt = optimizer[0]
                if len(optimizer) > 1 and isinstance(optimizer[1], str):
                    self.method = optimizer[1].lower()
                if len(optimizer) == 3:
                    self.batch_size = optimizer[2]
            elif isinstance(optimizer[0], str):
                name, lr = optimizer[:2]
                self._make_opt = lambda p: getattr(torch.optim, name.upper())(p, lr)
            else:
                raise ValueError("First element of optimizer tuple must be callable or str")
        else:
            raise ValueError(
                "optimizer must be None, callable, "
                "(name, lr) or (factory, method, batch_size)"
            )

        self._early = _EarlyStopper(**early_stopping) if early_stopping else None

        # ── runtime placeholders ───────────────────────────────────
        self.weights = None
        self.n_features = self.num_classes = None
        self.feature_mean_ = self.feature_std_ = None
        self._snapshots = {}
        self._early_stop_epoch = None

    # ── helpers ──
    def _init_weights(self):
        init = _VALID_INITS[self.weight_init]
        self.weights = torch.nn.Parameter(init((self.n_features, self.num_classes)))
        self.opt = self._make_opt([self.weights])
        self.optimizer = self.opt

    def _forward(self, X):           # logits → probas
        z = X @ self.weights
        return torch.sigmoid(z) if self.num_classes==1 else torch.softmax(z, dim=1)

    def _loss(self, X, y):
        pred = self._forward(X)
        loss = _bce(y,pred) if self.num_classes==1 else _ce(y,pred)
        return loss + (self.regularizer(self.weights) if self.regularizer else 0)

    # métricas --------------------------------------------------------
    def _metric_val(self, X, y):
        p = self._forward(X)
        if self.num_classes==1:
            if self.metric=="accuracy":   return _acc_bin(y,p)
            TP=((p>=.5)&(y==1)).sum(); FP=((p>=.5)&(y==0)).sum(); FN=((p<.5)&(y==1)).sum()
            if self.metric=="precision":  return TP/(TP+FP+_EPS)
            if self.metric=="recall":     return TP/(TP+FN+_EPS)
            prec = TP/(TP+FP+_EPS); rec = TP/(TP+FN+_EPS)
            return 2*prec*rec/(prec+rec+_EPS)
        # multiclase
        y_true = y.argmax(1); y_pred = p.argmax(1); k = self.num_classes
        if self.metric=="accuracy": return _acc_mc(y,p)
        metrics=[]
        for c in range(k):
            tp=((y_pred==c)&(y_true==c)).sum()
            fp=((y_pred==c)&(y_true!=c)).sum()
            fn=((y_pred!=c)&(y_true==c)).sum()
            prec=tp/(tp+fp+_EPS); rec=tp/(tp+fn+_EPS)
            if self.metric=="precision": metrics.append(prec)
            elif self.metric=="recall":  metrics.append(rec)
            else: metrics.append(2*prec*rec/(prec+rec+_EPS))
        return torch.stack(metrics).mean()

    def train(
        self,
        train_set: Tuple[np.ndarray, np.ndarray],
        *,
        val_set: Optional[Tuple[np.ndarray, np.ndarray]] = None,
        test_set: Optional[Tuple[np.ndarray, np.ndarray]] = None,
    ):
        """
        Ajusta el modelo y guarda internamente los datasets de entrenamiento
        (y opcionalmente validación/prueba) para que el ReportBuilder los
        recupere automáticamente. Ahora también captura:
        • feature_names (si X es DataFrame o array con dtype.names)
        • target_name   (si y es Series con .name)
        • class_names   (preservando el orden de aparición)
        """
        self._mlektic_t0 = _dt.now()
        try:
            # ---------- preparar X, y (numpy) ---------------------------------
            X_np, y_np = train_set

            # ⬇️  Guarda SIEMPRE el set de entrenamiento (para el reporte)
            self._mlektic_X_train = X_np
            self._mlektic_y_train = y_np
            if val_set is not None:
                self._mlektic_X_val,  self._mlektic_y_val  = val_set
            if test_set is not None:
                self._mlektic_X_test, self._mlektic_y_test = test_set

            # -------- nombres: features / target -------------------------------
            # features: DataFrame.columns  > ndarray.dtype.names  > _feature_names  > fallback
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

            # target name (Series.name, atributo interno o fallback)
            tname = None
            try:
                if hasattr(y_np, "name") and getattr(y_np, "name") is not None:
                    tname = str(getattr(y_np, "name"))
                elif hasattr(y_np, "_target_name"):
                    tname = str(getattr(y_np, "_target_name"))
            except Exception:
                pass
            self._target_name = tname or "y"

            # ---------- tensores -----------------------------------------------
            X = torch.tensor(np.asarray(X_np, dtype=np.float32), dtype=torch.float32)

            # ---------- estandarización ---------------------------------------
            if self.standardize:
                self.feature_mean_ = X.mean(0, keepdim=True)
                self.feature_std_  = X.std(0, keepdim=True) + 1e-8
                X = (X - self.feature_mean_) / self.feature_std_

            # ---------- intercepto --------------------------------------------
            if self.use_intercept:
                X = torch.cat([torch.ones(len(X), 1), X], 1)
            self.n_features = X.shape[1]

            # ---------- nombres de features (longitud coherente) ---------------
            n_no_bias = self.n_features - int(self.use_intercept)
            if not feat_names or len(feat_names) != n_no_bias:
                feat_names = [f"x{i+1}" for i in range(n_no_bias)]
            self.feature_names  = feat_names
            self._feature_names = feat_names

            # ---------- etiquetas (strings o numéricas no contiguas) ----------
            y_raw = np.asarray(y_np).ravel()
            self._class_label_to_index = None
            self._class_index_to_label = None
            self._class_names          = None

            uniq_vals, first_idx = np.unique(y_raw, return_index=True)
            order   = np.argsort(first_idx)                  # preserva orden de aparición
            classes = [uniq_vals[i] for i in order]
            lab2idx = {cls: i for i, cls in enumerate(classes)}
            idx2lab = {i: cls for i, cls in enumerate(classes)}
            y_idx   = np.array([lab2idx[val] for val in y_raw], dtype=np.int64)

            self._class_label_to_index = lab2idx
            self._class_index_to_label = idx2lab
            self._class_names          = [str(c) for c in classes]

            n_unique = len(np.unique(y_idx))
            self.num_classes = 1 if n_unique == 2 else n_unique

            if self.num_classes == 1:
                y = torch.tensor(y_idx.reshape(-1, 1), dtype=torch.float32)
            else:
                y_hot = np.zeros((len(y_idx), self.num_classes), np.float32)
                y_hot[np.arange(len(y_idx)), y_idx] = 1.0
                y = torch.tensor(y_hot, dtype=torch.float32)

            # ---------- inicialización / entrenamiento ------------------------
            self._init_weights()
            self._snapshots = {"start": self.weights.detach().cpu().numpy().copy()}
            self._early_stop_epoch = None
            hist_name = f"{self.metric}_history"

            if self.method == "lbfgs":
                def closure():
                    self.opt.zero_grad()
                    z = X @ self.weights
                    pred = torch.sigmoid(z) if self.num_classes == 1 else torch.softmax(z, dim=1)
                    if self.num_classes == 1:
                        eps = 1e-8; p = torch.clamp(pred, eps, 1 - eps)
                        loss = -(y * torch.log(p) + (1 - y) * torch.log(1 - p)).mean()
                    else:
                        eps = 1e-8; ps = torch.clamp(pred, eps, 1 - eps)
                        loss = -(y * torch.log(ps)).sum(1).mean()
                    if self.regularizer:
                        loss = loss + self.regularizer(self.weights)
                    loss.backward()
                    return loss

                for epoch in range(self.iterations):
                    loss_val = float(self.opt.step(closure))
                    with torch.no_grad():
                        z = X @ self.weights
                        pred = torch.sigmoid(z) if self.num_classes == 1 else torch.softmax(z, dim=1)
                        if self.num_classes == 1:
                            metric_val = ((pred >= 0.5) == y).float().mean().item() \
                                        if self.metric == "accuracy" else float(self._metric_val(X, y))
                        else:
                            metric_val = float(self._metric_val(X, y))
                    self.cost_history.append(loss_val)
                    self.metric_history.append(metric_val)
                    getattr(self, hist_name).append(metric_val)

                    if epoch == max(self.iterations // 2 - 1, 0):
                        self._snapshots["mid"] = self.weights.detach().cpu().clone().numpy()

                    if self._early and self._early(loss_val):
                        self._early_stop_epoch = epoch + 1
                        break

                self._snapshots["end"] = self.weights.detach().cpu().numpy().copy()
                return self

            if self.method in {"batch", "stochastic", "mini-batch", "mle"}:
                trainer = build_torch_trainer(
                    method        = self.method,
                    model         = self,
                    optimizer     = self.opt,
                    iterations    = self.iterations,
                    batch_size    = self.batch_size,
                    tol           = self.tol,
                    early_stopper = self._early,
                )
                trainer.run(X, y)
                if len(getattr(self, hist_name)) == 0:
                    getattr(self, hist_name).extend(self.metric_history)
                return self

            raise ValueError(f"Método '{self.method}' no soportado por este backend.")
        finally:
            self._mlektic_t1 = _dt.now()



    # ── pred / eval ──
    def _prep(self,x:Union[np.ndarray,list,float,Dict[str,float]]):
        if isinstance(x,dict): x=torch.tensor([x[n] for n in self.feature_names],dtype=torch.float32)
        elif isinstance(x,float): x=torch.tensor([x],dtype=torch.float32)
        else: x=torch.tensor(np.asarray(x,np.float32))
        if x.ndim==1: x=x.unsqueeze(0)
        if self.standardize: x=_standardize(x,self.feature_mean_,self.feature_std_)
        if self.use_intercept: x=torch.cat([torch.ones(len(x),1),x],1)
        return x
    
    def predict_prob(self,x): return self._forward(self._prep(x)).detach().numpy()

    def predict_class(self,x):
        p=self.predict_prob(x); return (p>=.5).astype(int).ravel() if self.num_classes==1 else p.argmax(1)
    
    # ── pred / eval ───────────────────────────────────────────────────────
    def eval(
        self,
        test_set: Tuple[np.ndarray, np.ndarray],
        metric: str = "accuracy",
        *,
        to_df: bool = False,
        role: str = "test",   # "test" (default) o "val" para registrar a voluntad
    ):
        """
        Evalúa el modelo sobre (X, y). Además registra el conjunto evaluado
        como 'test' (por defecto) o 'val' para que el ReportBuilder calcule
        el split automáticamente.
        """
        if metric not in _VALID_METRICS:
            raise ValueError(f"metric '{metric}' no soportada")

        orig_metric, self.metric = self.metric, metric

        # -------- preparar X / y (y registrar porción) ------------------
        X_np, y_np = test_set

        # ⬇️  Guarda para el reporte (sin afectar al entrenamiento)
        if role == "val":
            self._mlektic_X_val,  self._mlektic_y_val  = X_np, y_np
        else:
            self._mlektic_X_test, self._mlektic_y_test = X_np, y_np

        X = torch.tensor(np.asarray(X_np, dtype=np.float32), dtype=torch.float32)
        if self.standardize:
            X = (X - self.feature_mean_) / self.feature_std_
        if self.use_intercept:
            X = torch.cat([torch.ones(len(X), 1), X], 1)

        y_raw = np.asarray(y_np).ravel()
        if getattr(self, "_class_label_to_index", None) is not None:
            try:
                y_idx = np.array([self._class_label_to_index[val] for val in y_raw], dtype=np.int64)
            except KeyError:
                def _coerce(v):
                    if v in self._class_label_to_index: return self._class_label_to_index[v]
                    try:    return self._class_label_to_index[int(v)]
                    except Exception:
                        return self._class_label_to_index[float(v)]
                y_idx = np.array([_coerce(v) for v in y_raw], dtype=np.int64)
        else:
            uniq_vals, first_idx = np.unique(y_raw, return_index=True)
            order = np.argsort(first_idx)
            lab2idx = {uniq_vals[i]: i for i in order}
            y_idx = np.array([lab2idx[v] for v in y_raw], dtype=np.int64)

        if self.num_classes == 1:
            y = torch.tensor(y_idx.reshape(-1, 1), dtype=torch.float32)
        else:
            y_hot = np.zeros((len(y_idx), self.num_classes), np.float32)
            y_hot[np.arange(len(y_idx)), y_idx] = 1.0
            y = torch.tensor(y_hot, dtype=torch.float32)

        # -------- métricas ------------------------------------------------
        if metric == "confusion_matrix":
            if self.num_classes == 1:
                from .metrics_binary import confusion_matrix as bin_conf_mat
                with torch.no_grad():
                    z = X @ self.weights
                    p = torch.sigmoid(z).detach().numpy().ravel()
                self.metric = orig_metric
                return bin_conf_mat(y.numpy().ravel(), p, to_df=to_df)
            else:
                from .logreg_utils import calculate_confusion_matrix
                with torch.no_grad():
                    z  = X @ self.weights
                    ps = torch.softmax(z, dim=1).detach()
                self.metric = orig_metric
                # ⬅️ NUEVO: pasar nombres de clase para que el collector pueda rotular en español
                return calculate_confusion_matrix(
                    torch.tensor(y.numpy()), ps, to_df=to_df, class_names=self._class_names
                )

        with torch.no_grad():
            z = X @ self.weights
            if self.num_classes == 1:
                p = torch.sigmoid(z)
                if metric == "binary_crossentropy":
                    eps = 1e-8; pp = torch.clamp(p, eps, 1 - eps)
                    val = float(-(y * torch.log(pp) + (1 - y) * torch.log(1 - pp)).mean().item())
                else:
                    val = float(self._metric_val(X, y).item())
            else:
                ps = torch.softmax(z, dim=1)
                if metric == "binary_crossentropy":
                    raise ValueError("binary_crossentropy sólo aplica a problemas binarios")
                elif metric == "categorical_crossentropy":
                    eps = 1e-8; pps = torch.clamp(ps, eps, 1 - eps)
                    val = float(-(y * torch.log(pps)).sum(1).mean().item())
                else:
                    val = float(self._metric_val(X, y).item())

        self.metric = orig_metric
        return val

    
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
        Devuelve la matriz de pesos sin la fila de sesgo.

        • Binario   → shape ``(n_features, 1)``
        • Multiclase→ shape ``(n_features, n_classes)``
        """
        if self.weights is None:
            raise RuntimeError("Call train() before accessing parameters.")
        if self.use_intercept:
            return self.weights[1:].detach().numpy()
        return self.weights.detach().numpy()

    def get_intercept(self) -> Optional[np.ndarray]:
        """
        Devuelve el sesgo:

        • Binario   → escalar ``float``
        • Multiclase→ vector ``(n_classes,)``

        Si ``use_intercept=False`` devuelve ``None``.
        """
        if not self.use_intercept:
            return None
        if self.weights is None:
            raise RuntimeError("Call train() before accessing the intercept.")
        bias = self.weights[0]
        return (
            bias.detach().numpy().ravel()      # multiclase
            if self.num_classes and self.num_classes > 1
            else float(bias.detach().item())   # binario
        )

    # --------------------------- alias API ----------------------------
    def predict(self, x):
        """
        Alias de :py:meth:`predict_class` para mantener paridad de interfaz.
        """
        return self.predict_class(x)


    # ── serialización ──
    def save_model(self,f):
        data=dict(
            config=dict(
                backend="torch",use_intercept=self.use_intercept,standardize=self.standardize,
                n_features=self.n_features,num_classes=self.num_classes),
            weights=self.weights.detach().numpy().tolist(),
            cost_history=list(self.cost_history),metric_history=list(self.metric_history),
            feature_mean_=None if self.feature_mean_ is None else self.feature_mean_.detach().numpy().tolist(),
            feature_std_=None if self.feature_std_ is None else self.feature_std_.detach().numpy().tolist(),
        )
        Path(f).parent.mkdir(parents=True,exist_ok=True); json.dump(data,open(f,"w"))
        if self.verbose: print(f"✔ Model saved to {Path(f).resolve()}")

    @classmethod
    def from_file(cls,f):
        p=json.load(open(f)); cfg=p["config"]
        mdl=cls(use_intercept=cfg["use_intercept"],standardize=cfg["standardize"])
        mdl.n_features, mdl.num_classes = cfg["n_features"], cfg["num_classes"]
        mdl._init_weights(); mdl.weights.data=torch.tensor(p["weights"],dtype=torch.float32)
        mdl.cost_history=deque(p.get("cost_history",[])); mdl.metric_history=deque(p.get("metric_history",[]))
        if p.get("feature_mean_") is not None:
            mdl.feature_mean_=torch.tensor(p["feature_mean_"],dtype=torch.float32)
        if p.get("feature_std_") is not None:
            mdl.feature_std_ =torch.tensor(p["feature_std_"],dtype=torch.float32)
        mdl.feature_names=[f"x{i+1}" for i in range(mdl.n_features-int(mdl.use_intercept))]
        return mdl

# alias para el import dinámico
LogisticRegressionArchtImpl = LogisticRegressionArchtImpl