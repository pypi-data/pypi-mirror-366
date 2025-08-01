# mlektic/logistic_reg/logistic_regression_tf.py

from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Callable, Optional, Tuple, Union, Dict, Any

import numpy as np
import tensorflow as tf

from .logreg_utils import (
    calculate_categorical_crossentropy,
    calculate_binary_crossentropy,
    calculate_accuracy,
    calculate_precision,
    calculate_recall,
    calculate_f1_score,
    calculate_confusion_matrix,
)
from ..methods.trainers import build_trainer
from .metrics_binary import (
    accuracy as bin_acc,
    precision as bin_prec,
    recall as bin_rec,
    f1_score as bin_f1,
    confusion_matrix as bin_conf_mat,
)

# Constants
_VALID_METRICS = {"accuracy", "precision", "recall", "f1_score"}
_VALID_INITS: dict[str, Callable[[tuple[int, ...]], np.ndarray]] = {
    "zeros": lambda shape: np.zeros(shape, np.float32),
    "random_normal": lambda shape: np.random.randn(*shape).astype(np.float32) * 1e-2,
    "glorot": lambda shape: (
        np.random.randn(*shape).astype(np.float32) * np.sqrt(2.0 / sum(shape))
    ),
}

# Helper utilities
def _validate_method_vs_optimizer(method: str, batch_size: Optional[int]) -> None:
    """Warn if the training method / batch_size combination is incoherent.

    Args:
        method: Selected training strategy (``"batch"``, ``"mini-batch"``, …).
        batch_size: User‑supplied batch size or ``None``.

    Side effects:
        Emits a warning to *stdout* when the user passes a batch size but
        ``method=="batch"`` (the size will be ignored in that case).
    """
    if method == "batch" and batch_size is not None:
        print(
            "⚠️  batch_size will be ignored because method='batch'. "
            "Set method='mini-batch' if you want mini‑batch training."
        )


def _standardize(X: np.ndarray, mean_: np.ndarray, std_: np.ndarray) -> np.ndarray:
    """Apply feature‑wise z‑score standardisation.

    Args:
        X: Input design matrix ``(n_samples, n_features)``.
        mean_: Pre‑computed feature means (shape ``(1, n_features)``).
        std_:  Pre‑computed feature std‑devs (shape ``(1, n_features)``).

    Returns:
        The standardised matrix.
    """
    return (X - mean_) / std_


class _EarlyStopper:
    """Utility class implementing patience‑based early stopping.

    The instance is created by :class:`LogisticRegressionArcht` and injected
    into the concrete *trainer* so that the same logic is re‑used regardless of
    the optimisation algorithm.

    Args:
        patience: Number of epochs with no meaningful loss improvement after
            which the training loop will be interrupted.
        min_delta: Minimum absolute improvement (in loss) to be considered
            “meaningful”.
    """

    def __init__(self, *, patience: int, min_delta: float) -> None:
        self.patience = patience
        self.min_delta = min_delta
        self.best_loss: float = np.inf
        self._wait = 0

    #  __call__ is what the trainers invoke each epoch
    def __call__(self, current_loss: float) -> bool:
        """Return *True* when training should stop early."""
        if self.best_loss - current_loss > self.min_delta:
            self.best_loss = current_loss
            self._wait = 0
        else:
            self._wait += 1
        return self._wait >= self.patience



# Logistic‑Regression core
class LogisticRegressionArcht:
    """Versatile logistic regression (binary or soft‑max).

    The class focuses on model *architecture* and delegates optimisation to
    specialised *trainer* objects — see ``trainers.py``.  This decoupling
    allows you to plug any training strategy (SGD, LBFGS, Newton, etc.)
    without altering the public API.

    Attributes
    ----------
    weights:
        Trainable parameter matrix of shape ``(n_features, n_classes)`` stored
        as a **tf.Variable** so that TensorFlow can track gradients.
    cost_history, metric_history:
        ``deque`` objects storing the loss / metric value for each epoch
        (useful for plotting learning curves).
    feature_mean_, feature_std_:
        Arrays with per‑feature statistics when *standardisation* is enabled.
    feature_names:
        Auto‑generated names (``x1``, ``x2``, …) set after training; they allow
        prediction via *dict* inputs (e.g. ``predict_prob({"x1":0.2,"x2":0.8})``).

    Notes
    -----
    * The implementation is kept **framework‑agnostic** at the public level:
      end‑users interact through NumPy arrays.  TensorFlow comes into play
      internally only for gradient‑based trainers.
    * All tensors flowing through the model are explicitly cast to ``float32``
      in :pymeth:`_predict` to avoid dtype mismatches coming from external libs.
    """

    #  Constructor
    def __init__(
        self,
        *,
        iterations: int = 50,
        use_intercept: bool = True,
        verbose: bool = True,
        regularizer: Optional[Callable[[tf.Tensor], tf.Tensor]] = None,
        optimizer: Optional[Tuple[tf.optimizers.Optimizer, str, int]] = None,
        method: str = "mle",
        metric: str = "accuracy",
        tol: float = 1e-6,
        # ---- optional “v2” goodies ------------------------------------
        weight_init: str = "zeros",
        random_state: Optional[int] = None,
        early_stopping: Optional[Dict[str, Any]] = None,
        standardize: bool = False,
        ovr: bool = False,
    ):
        """Create an un‑trained logistic‑regression estimator.

        Args
        ----
        iterations:
            Maximum number of epochs (or LBFGS steps / Newton iterations,
            depending on *method*).
        use_intercept:
            Whether to prepend a bias column of ones to the design matrix.
        verbose:
            Print training progress every 10 % of the total epochs.
        regularizer:
            Optional callable that takes the *weight matrix* and returns a
            scalar penalty (L2, L1, …).
        optimizer:
            Triple *``(tf.keras.optimizers.Optimizer, method, batch_size)``*.
            If omitted, defaults to SGD with a 0.01 LR.
        method:
            Training strategy. One of ``"batch"``, ``"mini-batch"``,
            ``"stochastic"``, ``"mle"``, ``"lbfgs"``, ``"newton"``.
        metric:
            Default evaluation metric used both during training logs and in
            :pymeth:`eval` unless overwritten.
        tol:
            Numerical tolerance used by convergence checks in deterministic
            optimisers (MLE, LBFGS, Newton).
        weight_init:
            Key in ``_VALID_INITS`` specifying the initialiser for *weights*.
        random_state:
            Optional seed for full reproducibility (NumPy + TF).
        early_stopping:
            Dict such as ``{"patience":5,"min_delta":1e-4}``.  Ignored if
            *None*.
        standardize:
            Whether to z‑scale features on train and automatically apply the
            same transform on predict / eval.
        ovr:
            One‑Vs‑Rest decomposition for multiclass (not implemented yet).

        Raises
        ------
        ValueError
            If an unsupported *metric* is supplied.
        """
        # ---- reproducibility -----------------------------------------
        if random_state is not None:
            np.random.seed(random_state)
            tf.random.set_seed(random_state)

        # ---- store hyper‑params --------------------------------------
        self.iterations = iterations
        self.use_intercept = use_intercept
        self.verbose = verbose
        self.regularizer = regularizer
        self.metric = metric
        self.method = method
        self.tol = tol
        self.weight_init = weight_init
        self.early_cfg = early_stopping
        self.standardize = standardize
        self.ovr = ovr

        # ---- history containers -------------------------------------
        self.cost_history: deque[float] = deque()
        self.metric_history: deque[float] = deque()

        # ---- runtime placeholders -----------------------------------
        self.weights: tf.Variable | None = None
        self.n_features: int | None = None
        self.num_classes: int | None = None
        self.feature_mean_: Optional[np.ndarray] = None
        self.feature_std_: Optional[np.ndarray] = None

        # ---- optimiser / trainer defaults ---------------------------
        if optimizer:
            self.optimizer, self.method, self.batch_size = optimizer
        else:
            self.optimizer = tf.optimizers.SGD(learning_rate=0.01)
            self.batch_size = 32 if method == "mini-batch" else None

        _validate_method_vs_optimizer(self.method, self.batch_size)

        # ---- metric validation --------------------------------------
        if self.metric not in _VALID_METRICS:
            raise ValueError(
                f"Unsupported metric '{self.metric}'. "
                f"Choose from {_VALID_METRICS}."
            )

        # ---- early‑stopper instance ---------------------------------
        self._early_stopper: Optional[_EarlyStopper] = None
        if early_stopping is not None:
            self._early_stopper = _EarlyStopper(**early_stopping)

    #                      Internal helpers                           #
    @staticmethod
    def _softmax(z: tf.Tensor) -> tf.Tensor:  # noqa: D401
        """Numerically stable soft‑max."""
        return tf.nn.softmax(z)

    def _predict(self, x: tf.Tensor) -> tf.Tensor:
        """Low‑level forward pass used by every public predict helper."""
        x = tf.cast(x, tf.float32)               # make double‑sure dtypes match
        logits = tf.matmul(x, self.weights)
        return tf.nn.sigmoid(logits) if self.num_classes == 1 else self._softmax(logits)

    def _metric_fn(self, name: str):
        """Return a metric implementation matching the problem type."""
        if self.num_classes == 1:
            return {
                "accuracy": bin_acc,
                "precision": bin_prec,
                "recall": bin_rec,
                "f1_score": bin_f1,
            }[name]
        return {
            "accuracy": calculate_accuracy,
            "precision": calculate_precision,
            "recall": calculate_recall,
            "f1_score": calculate_f1_score,
        }[name]

    def _cost_function(self, X: tf.Tensor, Y: tf.Tensor) -> tf.Tensor:
        """Compute the negative log‑likelihood plus optional regulariser."""
        preds = self._predict(X)
        if self.num_classes == 1:
            loss = tf.reduce_mean(calculate_binary_crossentropy(Y, preds))
        else:
            loss = tf.reduce_mean(calculate_categorical_crossentropy(Y, preds))
        if self.regularizer is not None:
            loss += self.regularizer(self.weights)
        return loss

    def _compute_metric(self, X: tf.Tensor, Y: tf.Tensor) -> tf.Tensor:
        """Return the scalar metric selected in :pyattr:`metric`."""
        preds = self._predict(X)
        return self._metric_fn(self.metric)(Y, preds)

    #                           Training                              #
    def _init_weights(self) -> None:
        """Initialise *self.weights* and recreate the optimiser.

        The optimiser clone is crucial because `tf.keras` optimisers
        “remember” variables; re‑creating prevents *unknown‑variable* errors
        when training multiple models in a loop.
        """
        init_fn = _VALID_INITS.get(self.weight_init, _VALID_INITS["zeros"])
        w_np = init_fn((self.n_features, self.num_classes))
        # 👇 trainable=True de forma explícita (por robustez)
        self.weights = tf.Variable(w_np, dtype=tf.float32, trainable=True)

        # -------- clone optimiser (stateless copy) -------------------
        if isinstance(self.optimizer, tf.optimizers.Optimizer):
            opt_cls = type(self.optimizer)
            self.optimizer = opt_cls.from_config(self.optimizer.get_config())

    # ------------------------ standardisation helpers ---------------
    def _standardise_fit(self, X: np.ndarray) -> np.ndarray:
        """Fit scaler on *X* and return the transformed matrix."""
        if not self.standardize:
            return X
        self.feature_mean_ = X.mean(axis=0, keepdims=True)
        self.feature_std_ = X.std(axis=0, keepdims=True) + 1e-8
        return _standardize(X, self.feature_mean_, self.feature_std_)

    def _standardise_transform(self, X: np.ndarray) -> np.ndarray:
        """Transform *X* using previously fitted scaler."""
        if not self.standardize:
            return X
        if self.feature_mean_ is None or self.feature_std_ is None:
            raise RuntimeError("Standard scaler not fitted. Call train() first.")
        return _standardize(X, self.feature_mean_, self.feature_std_)

    # ---------------------------- public API -------------------------
    def train(self, train_set: Tuple[np.ndarray, np.ndarray]) -> "LogisticRegressionArcht":
        """Fit the model given a (features, labels) tuple.

        Args:
            train_set: Tuple ``(X, y)``.
                *X* must be a 2‑D **NumPy** array of dtype *float32* or
                convertible.  *y* can be:
                * 1‑D array of 0/1 for binary problems – it will be reshaped
                  to ``(n, 1)``.
                * Integer class labels for soft‑max – internally one‑hot coded.

        Returns:
            *self* to allow method chaining.
        """
        X, y = train_set
        X = X.astype(np.float32)
        y_raw = y.astype(np.float32)

        # ------------ scaler -----------------------------------------
        X = self._standardise_fit(X)

        # ------------ label preprocessing ----------------------------
        self.num_classes = int(len(np.unique(y_raw)))
        if self.num_classes == 2:
            self.num_classes = 1
            y_proc = y_raw.reshape(-1, 1)
        else:
            if self.ovr:
                raise NotImplementedError("OVR training is not implemented in v2 yet.")
            y_proc = tf.keras.utils.to_categorical(y_raw, self.num_classes)

        # ------------ intercept --------------------------------------
        if self.use_intercept:
            X = np.c_[np.ones((X.shape[0], 1)), X]
        self.n_features = X.shape[1]

        # ------------ weights + optimiser ----------------------------
        self._init_weights()

        # ------------ tensors & trainer ------------------------------
        X_tf = tf.convert_to_tensor(X, tf.float32)
        y_tf = tf.convert_to_tensor(y_proc, tf.float32)

        trainer = build_trainer(
            method=self.method,
            model=self,
            optimizer=self.optimizer,
            batch_size=self.batch_size,
            iterations=self.iterations,
            tol=self.tol,
            early_stopper=self._early_stopper,
        )
        trainer.run(X_tf, y_tf)

        # ------------ convenience for dict input ---------------------
        self.feature_names = [f"x{i+1}" for i in range(self.n_features - int(self.use_intercept))]
        return self

    #                           Prediction                            #
    def _prepare_input(self, x: Union[np.ndarray, list, float, Dict[str, float]]) -> np.ndarray:
        """Normalise and shape a single prediction sample.

        Accepts four input formats:

        1. ``dict`` — keys matching :pyattr:`feature_names`
        2. scalar ``float`` — only allowed for *one‑feature* models
        3. ``list`` of floats
        4. 1‑D or 2‑D ``np.ndarray``

        Returns
        -------
        np.ndarray
            2‑D row matrix with correct dtype and intercept column added
            (if enabled).
        """
        if isinstance(x, dict):
            if not hasattr(self, "feature_names"):
                raise ValueError("Model does not store feature_names; pass an array instead.")
            x = np.array([x[name] for name in self.feature_names], dtype=np.float32)
        elif isinstance(x, float):
            if self.n_features != 1:
                raise ValueError(
                    f"Model expects {self.n_features} features; "
                    "pass a list/array/dict with that many elements."
                )
            x = np.array([x], dtype=np.float32)
        elif isinstance(x, list):
            x = np.array(x, dtype=np.float32)
        elif isinstance(x, np.ndarray):
            x = x.astype(np.float32)

        if x.ndim == 1:
            x = x.reshape(1, -1)

        x = self._standardise_transform(x)

        if self.use_intercept:
            x = np.c_[np.ones((x.shape[0], 1)), x]

        if x.shape[1] != self.n_features:
            raise ValueError(f"Expected {self.n_features} features, got {x.shape[1]}")
        return x

    # --------------- public prediction helpers ----------------------
    def predict_prob(self, x_new: Union[np.ndarray, list, float, Dict[str, float]]):
        """Return class probabilities for *x_new*."""
        if self.weights is None:
            raise RuntimeError("Call train() before prediction.")
        X = self._prepare_input(x_new)
        return self._predict(tf.convert_to_tensor(X)).numpy()

    def predict_class(self, x_new: Union[np.ndarray, list, float, Dict[str, float]]):
        """Return the most likely class index (or 0/1 for binary)."""
        probs = self.predict_prob(x_new)
        return (probs >= 0.5).astype(int).ravel() if self.num_classes == 1 else np.argmax(probs, axis=1)

    #                           Evaluation                            #
    def eval(self, test_set: Tuple[np.ndarray, np.ndarray], metric: str, *, to_df: bool = True):
        """Evaluate *metric* on a hold‑out set.

        Args:
            test_set: Tuple ``(X_test, y_test)``.
            metric: Name of the metric; supports the same values as
                :pyattr:`_VALID_METRICS` plus
                ``"binary_crossentropy"``, ``"categorical_crossentropy"``,
                ``"confusion_matrix"``.
            to_df: Whether to return the confusion matrix as a *pandas* DataFrame
                (ignored for other metrics).

        Returns
        -------
        float | np.ndarray | pandas.DataFrame
            The metric value – type depends on the metric.
        """
        if metric not in _VALID_METRICS and metric not in {
            "categorical_crossentropy",
            "binary_crossentropy",
            "confusion_matrix",
        }:
            raise ValueError(f"Unsupported metric '{metric}'.")

        X, y_raw = test_set
        X = X.astype(np.float32)
        y_raw = y_raw.astype(np.float32)

        X = self._standardise_transform(X)
        if self.use_intercept:
            X = np.c_[np.ones((X.shape[0], 1)), X]

        if self.num_classes == 1:
            y_test = y_raw.reshape(-1, 1)
        else:
            y_test = tf.keras.utils.to_categorical(y_raw, self.num_classes)

        X_tf = tf.convert_to_tensor(X, tf.float32)
        y_tf = tf.convert_to_tensor(y_test, tf.float32)
        y_pred = self._predict(X_tf)

        # ---- dispatch -----------------------------------------------
        if self.num_classes == 1:
            binary_metrics = {
                "accuracy": bin_acc,
                "precision": bin_prec,
                "recall": bin_rec,
                "f1_score": bin_f1,
                "confusion_matrix": lambda yt, yp: bin_conf_mat(yt, yp, to_df=to_df),
                "binary_crossentropy": lambda yt, yp: float(
                    tf.reduce_mean(
                        calculate_binary_crossentropy(
                            tf.convert_to_tensor(yt), tf.convert_to_tensor(yp)
                        )
                    ).numpy()
                ),
            }
            return binary_metrics[metric](y_test, y_pred.numpy())

        multiclass_metrics = {
            "categorical_crossentropy": calculate_categorical_crossentropy,
            "binary_crossentropy": calculate_binary_crossentropy,
            "accuracy": calculate_accuracy,
            "precision": calculate_precision,
            "recall": calculate_recall,
            "f1_score": calculate_f1_score,
            "confusion_matrix": lambda yt, yp: calculate_confusion_matrix(yt, yp, to_df=to_df),
        }
        result = multiclass_metrics[metric](y_tf, y_pred)
        if metric == "confusion_matrix":
            return result
        return float(tf.reduce_mean(result).numpy())
    
    def get_cost_history(self, *, as_list: bool = True):
        """
        Devuelve la traza de costes (loss) registrada durante el entrenamiento.

        Parameters
        ----------
        as_list : bool, default True
            • True  → convierte el deque interno a una lista estándar  
            • False → devuelve el deque directamente

        Returns
        -------
        list | collections.deque
            Secuencia de valores de pérdida, una entrada por epoch / iteración.
        """
        return list(self.cost_history) if as_list else self.cost_history

    # (opcional) la gemela para la métrica principal
    def get_metric_history(self, *, as_list: bool = True):
        """Acceso a self.metric_history con la misma filosofía que arriba."""
        return list(self.metric_history) if as_list else self.metric_history    

    #                        User utilities                           #
    def set_metric(self, metric: str) -> None:
        """Change the *default* training metric on the fly."""
        if metric not in _VALID_METRICS:
            raise ValueError(f"Unsupported metric '{metric}'. Choose from {_VALID_METRICS}.")
        self.metric = metric

    def summary(self) -> str:
        """Return a one‑page textual summary of the model."""
        lines = [
            "LogisticRegressionArcht summary",
            "────────────────────────────────────────",
            f"n_features      : {self.n_features}",
            f"num_classes     : {self.num_classes}",
            f"iterations run  : {len(self.cost_history)}",
            f"final loss      : {self.cost_history[-1]:.6f}" if self.cost_history else "final loss      : n/a",
            f"final {self.metric} : {self.metric_history[-1]:.4f}" if self.metric_history else "",
            f"weight init     : {self.weight_init}",
            f"standardize     : {self.standardize}",
            f"early stopping  : {bool(self._early_stopper)}",
        ]
        return "\n".join(filter(bool, lines))

    # --------------------- parámetros e intercepto ---------------------
    def get_parameters(self) -> np.ndarray:
        """
        Devuelve los pesos sin la fila de sesgo.

        Raises
        ------
        RuntimeError
            Si el modelo aún no ha sido entrenado.
        """
        if self.weights is None:
            raise RuntimeError("Call train() before accessing parameters.")
        if self.use_intercept:
            return self.weights[1:].numpy()
        return self.weights.numpy()

    def get_intercept(self):
        """
        Devuelve el sesgo:

        • Binario   → escalar
        • Multiclase→ vector ``(n_classes,)``

        Si ``use_intercept=False`` devuelve ``None``.
        """
        if not self.use_intercept:
            return None
        if self.weights is None:
            raise RuntimeError("Call train() before accessing the intercept.")
        bias = self.weights[0]
        return (
            bias.numpy().ravel()                 # multiclase
            if self.num_classes and self.num_classes > 1
            else float(bias.numpy())             # binario
        )

    # --------------------------- alias API ----------------------------
    def predict(self, x_new):
        """
        Atajo que devuelve la clase más probable (‒igual que *predict_class*‒).
        """
        return self.predict_class(x_new)


    #                       Serialization                             #
    def save_model(self, filepath: str) -> None:
        """Persist the trained model to *filepath* as a single JSON file.

        The snapshot stores hyper‑parameters, learned weights, scaler
        statistics and the full training history so that
        :pyclass:`LogisticRegressionArcht.from_file` can fully restore the
        estimator.

        Parameters
        ----------
        filepath:
            Destination path; parent directories are created automatically.
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "config": {
                "use_intercept": self.use_intercept,
                "method": self.method,
                "metric": self.metric,
                "weight_init": self.weight_init,
                "standardize": self.standardize,
                "n_features": self.n_features,
                "num_classes": self.num_classes,
                "feature_mean_": None
                if self.feature_mean_ is None
                else self.feature_mean_.tolist(),
                "feature_std_": None
                if self.feature_std_ is None
                else self.feature_std_.tolist(),
            },
            "weights": None if self.weights is None else self.weights.numpy().tolist(),
            "cost_history": list(self.cost_history),
            "metric_history": list(self.metric_history),
        }

        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        if self.verbose:
            print(f"✔ Model saved to {path.resolve()}")

    # ---------------------------- loading helpers -------------------
    def load_model_into(self, filepath: str) -> None:
        """Restore a snapshot *onto the current instance* (in‑place)."""
        path = Path(filepath)
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        cfg = payload["config"]

        # -------- basic sanity checks -------------------------------
        if cfg["use_intercept"] != self.use_intercept:
            raise ValueError("Intercept setting mismatch.")
        if cfg["n_features"] != self.n_features:
            raise ValueError("Number‑of‑features mismatch.")
        if cfg["num_classes"] != self.num_classes:
            raise ValueError("Number‑of‑classes mismatch.")

        # -------- restore weights & history -------------------------
        self.weights = tf.Variable(np.array(payload["weights"], np.float32))
        self.cost_history = deque(payload.get("cost_history", []))
        self.metric_history = deque(payload.get("metric_history", []))

        if self.standardize:
            self.feature_mean_ = (
                None
                if cfg["feature_mean_"] is None
                else np.array(cfg["feature_mean_"], np.float32)
            )
            self.feature_std_ = (
                None
                if cfg["feature_std_"] is None
                else np.array(cfg["feature_std_"], np.float32)
            )

        if self.verbose:
            print(f"✔ Model state loaded from {path.resolve()}")

    # ----------------------- factory constructor --------------------
    @classmethod
    def from_file(cls, filepath: str) -> "LogisticRegressionArcht":
        """Instantiate a new object directly from a saved snapshot."""
        path = Path(filepath)
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        cfg = payload["config"]

        model = cls(
            use_intercept=cfg["use_intercept"],
            method=cfg["method"],
            metric=cfg["metric"],
            weight_init=cfg["weight_init"],
            standardize=cfg["standardize"],
        )

        # Allocate correct shapes, then reuse load_model_into
        model.n_features = cfg["n_features"]
        model.num_classes = cfg["num_classes"]
        model._init_weights()
        model.load_model_into(filepath)
        return model

LogisticRegressionArchtImpl = LogisticRegressionArcht
