# mlektic/linear_reg/linear_regression_archt.py

from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Callable, Optional, Tuple, Union, Dict, Any

import numpy as np
import tensorflow as tf

from ..methods.trainers import build_trainer             
from .linreg_utils import (                      
    calculate_mse, calculate_rmse, calculate_mae,
    calculate_mape, calculate_r2,
    calculate_pearson_correlation as calculate_corr,
)

# Constants
_VALID_METRICS = {"mse", "rmse", "mae", "mape", "r2", "corr"}
_VALID_INITS: dict[str, Callable[[tuple[int, ...]], np.ndarray]] = {
    "zeros": lambda shape: np.zeros(shape, np.float32),
    "random_normal": lambda shape: np.random.randn(*shape).astype(np.float32) * 1e-2,
    "glorot": lambda shape: (
        np.random.randn(*shape).astype(np.float32) * np.sqrt(2.0 / sum(shape))
    ),
}

# Helper utilities
def _validate_method_vs_optimizer(method: str, batch_size: Optional[int]) -> None:
    """
    Emit a runtime warning when *method* and *batch_size* are incoherent.

    Parameters
    ----------
    method : str
        Name of the training strategy chosen by the user
        (``"batch"``, ``"mini-batch"``, …).
    batch_size : int or None
        The batch size supplied in ``optimizer=(opt, method, batch_size)`` or
        *None* if not provided.

    Notes
    -----
    * The function does **not** raise; it only prints a message so that the
      caller (the model constructor) can proceed without aborting.
    """    
    if method == "batch" and batch_size is not None:
        print(
            "⚠️  batch_size will be ignored because method='batch'. "
            "Set method='mini-batch' if you want mini‑batch training."
        )


def _standardize(X: np.ndarray, mean_: np.ndarray, std_: np.ndarray) -> np.ndarray:
    """
    Apply a feature‑wise z‑score normalisation.

    Parameters
    ----------
    X : ndarray of shape ``(n_samples, n_features)``
        The raw design matrix.
    mean_ : ndarray of shape ``(1, n_features)``
        Mean value per feature.
    std_ : ndarray of shape ``(1, n_features)``
        Standard deviation per feature.

    Returns
    -------
    ndarray
        Standardised copy of *X* (original array is **not** modified).
    """    
    return (X - mean_) / std_


class _EarlyStopper:
    """
    Patience‑based early‑stopping helper shared by all trainers.

    The logic mirrors the one in the logistic‑regression module so that both
    estimators expose identical behaviour.

    Parameters
    ----------
    patience : int
        Number of consecutive epochs without a *meaningful* loss improvement
        after which training will be interrupted.
    min_delta : float
        Minimum absolute decrease in the monitored loss to be considered
        meaningful.

    Examples
    --------
    The trainer simply calls the instance at the end of each epoch::

        stopper = _EarlyStopper(patience=5, min_delta=1e-4)
        for epoch in range(max_epochs):
            …
            if stopper(current_loss):
                break
    """

    def __init__(self, *, patience: int, min_delta: float) -> None:
        self.patience = patience
        self.min_delta = min_delta
        self.best_loss: float = np.inf
        self._wait = 0

    def __call__(self, current_loss: float) -> bool:
        """
        Decide whether the external loop should stop.

        Returns
        -------
        bool
            *True* if the patience counter has been exceeded, *False* otherwise.
        """        
        if self.best_loss - current_loss > self.min_delta:
            self.best_loss = current_loss
            self._wait = 0
        else:
            self._wait += 1
        return self._wait >= self.patience


# Linear‑Regression core
class LinearRegressionArcht:
    """
    Flexible linear‑regression estimator with a unified high‑level API.

    The class offers both a **closed‑form solver** (normal equation) and a set
    of iterative, gradient‑based trainers re‑used from the *logistic* module
    (batch GD, SGD, mini‑batch, etc.).  This reuse keeps the public interface
    identical across *mlektic* models and reduces the maintenance burden.

    Attributes
    ----------
    weights : tf.Variable or None
        Weight matrix of shape ``(n_features, 1)`` once the model is trained.
    cost_history, metric_history : deque
        Per‑epoch loss / metric values, useful for learning‑curve plots.
    feature_mean_, feature_std_ : ndarray or None
        Stored statistics when *standardise=True*.
    feature_names : list[str]
        Auto‑generated names (``x1``, ``x2``, …) created after training so that
        predictions can be made from a *dict* of values.

    See Also
    --------
    mlektic.logistic_reg.LogisticRegressionArcht
        The classification counterpart sharing the same architecture.
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
        method: str = "least_squares",
        metric: str = "mse",
        tol: float = 1e-6,
        # ---- extras for v2 -------------------------------------------
        weight_init: str = "zeros",
        random_state: Optional[int] = None,
        early_stopping: Optional[Dict[str, Any]] = None,
        standardize: bool = False,
    ):
        """
        Create an *untrained* LinearRegressionArcht instance.

        Parameters
        ----------
        iterations : int, default=50
            Maximum number of optimisation steps for gradient‑based methods.
            Ignored when *method="least_squares"*.
        use_intercept : bool, default=True
            Whether to prepend a bias column of ones to the design matrix.
        verbose : bool, default=True
            Print training progress every ~10 % of the total epochs.
        regularizer : callable or None
            A function that takes the **weights** tensor and returns a scalar
            penalty (e.g. L2 or L1).  The value is added to the loss.
        optimizer : tuple(Optimizer, str, int) or None
            Triple ``(tf.keras.optimizers.Optimizer, method, batch_size)``.
            When *None*, the default is SGD with a learning‑rate of **0.01**.
        method : {"least_squares", "batch", "stochastic", "mini-batch", "mle"}
            Training strategy.  Second‑order methods such as *LBFGS* or
            *Newton* are **not** available because the generic trainer assumes
            a classification loss.
        metric : {"mse", "rmse", "mae", "mape", "r2", "corr"}, default="mse"
            Default evaluation metric used by :pymeth:`eval`.
        tol : float, default=1e‑6
            Convergence tolerance for iterative solvers that implement their
            own ||Δw|| or Δloss criteria (currently *mle*).
        weight_init : {"zeros", "random_normal", "glorot"}, default="zeros"
            Initialiser for *weights* when an iterative trainer is used.
        random_state : int or None
            Global seed for NumPy **and** TensorFlow – guarantees
            reproducibility of weight initialisation and shuffle operations.
        early_stopping : dict or None
            Example ``{"patience":5, "min_delta":1e-4}``.  Ignored if *None*.
        standardize : bool, default=False
            Apply z‑score scaling to *X* during *fit*; statistics are stored
            and re‑used in *predict*/*eval*.

        Raises
        ------
        ValueError
            If *metric* or *method* are not among the supported options.
        """        
        # reproducibility
        if random_state is not None:
            np.random.seed(random_state)
            tf.random.set_seed(random_state)

        # store hyper‑params
        self.iterations = iterations
        self.use_intercept = use_intercept
        self.verbose = verbose
        self.regularizer = regularizer
        self.metric = metric
        self.method = method
        self.tol = tol
        self.weight_init = weight_init
        self.standardize = standardize
        self.early_cfg = early_stopping

        # histories
        self.cost_history: deque[float] = deque()
        self.metric_history: deque[float] = deque()

        # runtime placeholders
        self.weights: tf.Variable | None = None
        self.n_features: int | None = None
        self.feature_mean_: Optional[np.ndarray] = None
        self.feature_std_: Optional[np.ndarray] = None

        # optimiser defaults
        if optimizer:
            self.optimizer, self.method, self.batch_size = optimizer
        else:
            self.optimizer = tf.optimizers.SGD(learning_rate=0.01)
            self.batch_size = 32 if method == "mini-batch" else None

        _validate_method_vs_optimizer(self.method, self.batch_size)

        if self.metric not in _VALID_METRICS:
            raise ValueError(f"Unsupported metric '{self.metric}'. Choose from {_VALID_METRICS}.")
        
        _VALID_METHODS = {
            "least_squares", "batch", "stochastic", "mini-batch", "mle"
        }
        if self.method not in _VALID_METHODS:
            raise ValueError(
                f"Unsupported method '{self.method}'. "
                f"Choose from {_VALID_METHODS}."
            )

        self._early_stopper: Optional[_EarlyStopper] = None
        if early_stopping is not None:
            self._early_stopper = _EarlyStopper(**early_stopping)

    #                      Internal helpers                           #
    @staticmethod
    def _metric_fn(name: str):
        """
        Map a *metric* string to its implementation.

        The returned function always expects **TensorFlow tensors** so that it
        can be composed with the rest of the computational graph.

        Parameters
        ----------
        name : str
            Key in :data:`_VALID_METRICS`.

        Returns
        -------
        Callable[[tf.Tensor, tf.Tensor], tf.Tensor]
            A vectorised metric function.
        """

        return {
            "mse":   calculate_mse,
            "rmse":  calculate_rmse,
            "mae":   calculate_mae,
            "mape":  calculate_mape,
            "r2":    calculate_r2,
            "corr":  calculate_corr,
        }[name]

    # --------------------- loss / metric helpers ---------------------
    def _predict(self, x: tf.Tensor) -> tf.Tensor:
        """
        Low‑level forward pass (no standardisation, no intercept handling).

        Parameters
        ----------
        x : tf.Tensor
            Design matrix already cast to *float32* and with the correct
            number of columns.

        Returns
        -------
        tf.Tensor
            Raw model output of shape ``(n_samples, 1)``.
        """        
        x = tf.cast(x, tf.float32)
        return tf.matmul(x, self.weights)

    def _cost_function(self, X: tf.Tensor, Y: tf.Tensor) -> tf.Tensor:
        """
        Calculate the training loss used by *gradient‑based* trainers.

        The loss is **MSE + regulariser** (if provided).

        Returns
        -------
        tf.Tensor
            Scalar tensor – mean over the batch.
        """        
        preds = self._predict(X)
        loss = tf.reduce_mean(calculate_mse(Y, preds))
        if self.regularizer is not None:
            loss += self.regularizer(self.weights)
        return loss

    def _compute_metric(self, X: tf.Tensor, Y: tf.Tensor) -> tf.Tensor:
        """
        Evaluate the current *metric* on a mini‑batch.

        Returns
        -------
        tf.Tensor
            Scalar tensor – mean metric value.
        """        
        preds = self._predict(X)
        return tf.reduce_mean(self._metric_fn(self.metric)(Y, preds))

    # ----------------- standardisation helpers -----------------------
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

    # ------------------ weight initialisation ------------------------
    def _init_weights(self) -> None:
        """
        Allocate :pyattr:`weights` and reset the optimiser state.

        The initial weight matrix is created according to the strategy in
        :data:`_VALID_INITS`.  Because *Keras* optimisers keep internal
        momentum/slot variables that are **tied** to the first variables they
        see, the optimiser is *cloned* from its configuration so that no stale
        state leaks from previous training runs (for instance when fitting
        several models in a loop).

        Notes
        -----
        * The method must be called **after** :pyattr:`n_features` is known.
        * Weight dtype is always forced to ``float32`` to be compatible with
          TensorFlow’s default precision.
        """        
        init_fn = _VALID_INITS.get(self.weight_init, _VALID_INITS["zeros"])
        w_np = init_fn((self.n_features, 1))
        self.weights = tf.Variable(w_np, dtype=tf.float32)

        # reset optimiser state
        if isinstance(self.optimizer, tf.optimizers.Optimizer):
            self.optimizer = type(self.optimizer).from_config(self.optimizer.get_config())

    #                           Training                              #
    def _train_least_squares(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Fit the model with the closed‑form normal equation.

        The solution is given by

        .. math::

            w = \\bigl( X^{\\top} X \\bigr)^{-1} X^{\\top} y

        which minimises the Mean‑Squared Error (MSE) in a single step.

        Parameters
        ----------
        X : ndarray of shape ``(n_samples, n_features)``
            Design matrix **after** optional standardisation and optional
            intercept augmentation.
        y : ndarray of shape ``(n_samples,)`` or ``(n_samples, 1)``
            Target vector.

        Side effects
        ------------
        * Sets :pyattr:`weights` with the analytical solution.
        * Appends the *final MSE* to :pyattr:`cost_history` so that learning
          curves remain consistent with those produced by iterative trainers.
        * Prints a confirmation line when :pyattr:`verbose` is *True*.
        """        
        Xt = tf.transpose(X)
        w = tf.linalg.solve(Xt @ X, Xt @ y.reshape(-1, 1))
        self.weights = tf.cast(w, tf.float32)
        mse_end = calculate_mse(tf.convert_to_tensor(y.reshape(-1,1)),
                            tf.convert_to_tensor(X @ self.weights)).numpy()
        self.cost_history.append(float(mse_end))    
        if self.verbose:
            print("✔ Model trained with closed " \
            "‑form normal equation.")

    def train(self, train_set: Tuple[np.ndarray, np.ndarray]) -> "LinearRegressionArcht":
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
        y = y.astype(np.float32)

        X = self._standardise_fit(X)

        if self.use_intercept:
            X = np.c_[np.ones((X.shape[0], 1)), X]
        self.n_features = X.shape[1]

        if self.method == "least_squares":
            self._train_least_squares(X, y)
        else:

            # ---------- GD / LBFGS / Newton via shared trainer ----------
            self._init_weights()

            X_tf = tf.convert_to_tensor(X, tf.float32)
            y_tf = tf.convert_to_tensor(y.reshape(-1, 1), tf.float32)

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
        self.feature_names = [
            f"x{i+1}" for i in range(self.n_features - int(self.use_intercept))
        ]
        return self

    #                           Prediction                            #
    def _prepare_input(self, x: Union[np.ndarray, list, float, Dict[str, float]]) -> np.ndarray:
        """
        Normalise, reshape and augment a single sample before prediction.

        The method accepts four different *user‑facing* formats and converts
        them into the 2‑D design matrix expected by :pymeth:`_predict`.

        Parameters
        ----------
        x : {ndarray, list, float, dict}
            * **dict** – Keys must match :pyattr:`feature_names` generated
              after training.  Example:
              ``{"x1": 0.2, "x2": -1.7}``.
            * **float** – Allowed **only** when the model was trained on a
              single feature.  The scalar is promoted to shape ``(1, 1)``.
            * **list** – A Python list of raw feature values.
            * **ndarray** – Either 1‑D (promoted to a row) or 2‑D.

        Returns
        -------
        ndarray
            Array of shape ``(1, n_features)`` – already standardised and with
            the intercept column of ones appended when
            :pyattr:`use_intercept` is *True*.

        Raises
        ------
        ValueError
            If the supplied input format is inconsistent with the model
            topology (wrong number of features, missing ``feature_names``,
            scalar given to a multi‑feature model, etc.).
        """        
        if isinstance(x, dict):
            if not hasattr(self, "feature_names"):
                raise ValueError("Model does not store feature_names; pass an array instead.")
            x = np.array([x[n] for n in self.feature_names], np.float32)
        elif isinstance(x, float):
            if self.n_features != 1:
                raise ValueError(
                    f"Model expects {self.n_features} features; "
                    "pass a list/array/dict with that many elements."
                )
            x = np.array([x], np.float32)
        elif isinstance(x, list):
            x = np.array(x, np.float32)
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

    def predict(self, x_new: Union[np.ndarray, list, float, Dict[str, float]]) -> np.ndarray:
        """Return model output(s) for *x_new*."""
        if self.weights is None:
            raise RuntimeError("Call train() before prediction.")
        X = self._prepare_input(x_new)
        return self._predict(tf.convert_to_tensor(X)).numpy()

    #                            Evaluation                           #
    def eval(self, test_set: Tuple[np.ndarray, np.ndarray], metric: str | None = None) -> float:
        """Evaluate the model on a hold out set using *metric*."""
        metric = metric or self.metric
        if metric not in _VALID_METRICS:
            raise ValueError(f"Unsupported metric '{metric}'. Choose from {_VALID_METRICS}.")

        X, y = test_set
        X = X.astype(np.float32)
        y = y.astype(np.float32)

        X = self._standardise_transform(X)
        if self.use_intercept:
            X = np.c_[np.ones((X.shape[0], 1)), X]

        X_tf = tf.convert_to_tensor(X, tf.float32)
        y_tf = tf.convert_to_tensor(y.reshape(-1, 1), tf.float32)
        y_pred = self._predict(X_tf)

        fn = self._metric_fn(metric)
        return float(tf.reduce_mean(fn(y_tf, y_pred)).numpy())
    
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

    #                       Introspection utils                       #
    def get_parameters(self) -> np.ndarray:
        """Return the weight vector (bias excluded)."""
        if self.use_intercept:
            return self.weights[1:].numpy()
        return self.weights.numpy()

    def get_intercept(self) -> float | None:
        """Return the bias term if present."""
        if self.use_intercept:
            return float(self.weights[0].numpy())
        return None

    def summary(self) -> str:
        """Textual one pager."""
        lines = [
            "LinearRegressionArcht summary",
            "────────────────────────────────────────",
            f"n_features      : {self.n_features}",
            f"iterations run  : {len(self.cost_history)}",
            f"final loss (MSE): {self.cost_history[-1]:.6f}" if self.cost_history else "final loss : n/a",
            f"standardize     : {self.standardize}",
            f"early stopping  : {bool(self._early_stopper)}",
        ]
        return "\n".join(filter(bool, lines))

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
                "backend": "tf",             
                "use_intercept": self.use_intercept,
                "weight_init": self.weight_init,
                "standardize": self.standardize,
                "n_features": self.n_features,
            },
            "weights": None if self.weights is None else self.weights.numpy().tolist(),
            "cost_history": list(self.cost_history),
            "feature_mean_": None if self.feature_mean_ is None else self.feature_mean_.tolist(),
            "feature_std_": None if self.feature_std_ is None else self.feature_std_.tolist(),
        }
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        if self.verbose:
            print(f"✔ Model saved to {path.resolve()}")

    def load_model(self, filepath: str) -> None:
        """Restore a snapshot *onto the current instance* (in‑place)."""        
        path = Path(filepath)
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        cfg = payload["config"]
        if cfg["use_intercept"] != self.use_intercept:
            raise ValueError("Intercept setting mismatch.")

        self.n_features = cfg["n_features"]
        self._init_weights()  # allocate correct shape
        self.weights.assign(np.array(payload["weights"], dtype=np.float32))
        self.cost_history = deque(payload.get("cost_history", []))

        # Restore standardization attributes if available
        self.feature_mean_ = (
            np.array(payload.get("feature_mean_"), dtype=np.float32)
            if payload.get("feature_mean_") is not None else None
        )
        self.feature_std_ = (
            np.array(payload.get("feature_std_"), dtype=np.float32)
            if payload.get("feature_std_") is not None else None
        )

        self.feature_names = [
            f"x{i+1}" for i in range(self.n_features - int(self.use_intercept))
        ]

        if self.verbose:
            print(f"✔ Model state loaded from {path.resolve()}")


    # factory constructor
    @classmethod
    def from_file(cls, filepath: str) -> "LinearRegressionArcht":
        """Instantiate directly from a saved JSON snapshot."""
        path = Path(filepath)
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        cfg = payload["config"]

        model = cls(
            use_intercept=cfg["use_intercept"],
            weight_init=cfg["weight_init"],
            standardize=cfg["standardize"],
        )
        model.n_features = cfg["n_features"]
        model._init_weights()
        model.load_model(filepath)
        model.feature_names = [
            f"x{i+1}" for i in range(model.n_features - int(model.use_intercept))
        ]
        return model

# alias for wrapper
LinearRegressionArchtImpl = LinearRegressionArcht 
del LinearRegressionArcht