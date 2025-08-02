from __future__ import annotations
import abc
from typing import Dict, Type, Optional, Callable

import numpy as np
import tensorflow as tf

try:
    import tensorflow_probability as tfp  # Optional, only for LBFGS
except ImportError:                       # pragma: no cover
    tfp = None


# Base class

class BaseTrainer(abc.ABC):
    """Abstract façade for all concrete training strategies.

    Parameters
    ----------
    model:
        Reference to the *owning* :class:`~mlektic.logistic_reg.LogisticRegressionArcht`
        instance.  Trainers read its attributes and write back to
        ``model.weights`` plus the ``cost_history`` / ``metric_history`` deques.
    optimizer:
        Any Keras/TensorFlow optimiser (SGD, Adam, …).  For second order
        trainers that do **not** rely on TF (e.g. ``NewtonTrainer``) this may
        go unused but is kept for API consistency.
    iterations:
        Maximum number of epochs / steps / iterations, depending on the
        concrete algorithm.
    batch_size:
        Only relevant for ``MiniBatchTrainer``; ignored elsewhere.
    tol:
        Numerical tolerance employed by algorithms with their *own*
        convergence test not to be confused with the *early stopping*
        tolerance inside the model.
    early_stopper:
        Callable injected by the model that returns *True* when the external
        early stopping criterion is met (patience + min_delta logic).

    Notes
    -----
    * The class maintains two helper methods, :pymeth:`_log` and
      :pymeth:`_update_history`, so that subclasses can focus on the maths.
    """

    def __init__(
        self,
        *,
        model,
        optimizer: tf.optimizers.Optimizer,
        iterations: int,
        batch_size: int | None = None,
        tol: float = 1e-6,
        early_stopper: Optional[Callable[[float], bool]] = None,
    ):
        self.model = model
        self.optimizer = optimizer
        self.iterations = iterations
        self.batch_size = batch_size
        self.tol = tol
        self.early_stopper = early_stopper

    # ------------------------------------------------------------------ #
    #  Logging & history helpers
    # ------------------------------------------------------------------ #
    def _log(self, epoch: int, loss_val: float, metric_val: float) -> None:
        """Print a progress line every 10 % of the total epochs."""
        if self.model.verbose and (epoch + 1) % max(1, self.iterations // 10) == 0:
            print(
                f"Epoch {epoch + 1:>4d} | "
                f"Loss={loss_val:.6f} | "
                f"{self.model.metric.capitalize()}={metric_val:.4f}"
            )

    def _update_history(self, loss_val: float, metric_val: float) -> None:
        """Append the current stats to the model's history deques."""
        self.model.cost_history.append(loss_val)
        self.model.metric_history.append(metric_val)

    # ------------------------------------------------------------------ #
    #  API every subclass must implement
    # ------------------------------------------------------------------ #
    @abc.abstractmethod
    def run(self, X: tf.Tensor, Y: tf.Tensor) -> None:  # pragma: no cover
        """Execute the training loop and update ``model.weights`` in place."""
        raise NotImplementedError


# Concrete implementations
class BatchTrainer(BaseTrainer):
    """Full batch gradient descent."""

    def run(self, X, Y):
        for epoch in range(self.iterations):
            with tf.GradientTape() as tape:
                # 👇 explícitamente observamos los pesos para evitar grads=None
                tape.watch(self.model.weights)
                loss = self.model._cost_function(X, Y)
                metric = self.model._compute_metric(X, Y)
            grads = tape.gradient(loss, [self.model.weights])
            # (defensa) si por alguna razón sigue llegando None, lo reemplazamos por ceros
            if grads[0] is None:
                grads[0] = tf.zeros_like(self.model.weights)
            self.optimizer.apply_gradients(zip(grads, [self.model.weights]))

            self._update_history(float(loss), float(metric))
            self._log(epoch, float(loss), float(metric))

            if self.early_stopper and self.early_stopper(float(loss)):
                if self.model.verbose:
                    print(f"⏹ Early stopping at epoch {epoch + 1}")
                break


class StochasticTrainer(BaseTrainer):
    """Stochastic gradient descent (update after every single sample)."""

    def run(self, X, Y):
        n = X.shape[0]
        for epoch in range(self.iterations):
            epoch_loss = epoch_metric = 0.0
            for i in range(n):
                x_i, y_i = X[i : i + 1], Y[i : i + 1]
                with tf.GradientTape() as tape:
                    tape.watch(self.model.weights)
                    loss = self.model._cost_function(x_i, y_i)
                    metric = self.model._compute_metric(x_i, y_i)
                grads = tape.gradient(loss, [self.model.weights])
                if grads[0] is None:
                    grads[0] = tf.zeros_like(self.model.weights)
                self.optimizer.apply_gradients(zip(grads, [self.model.weights]))
                epoch_loss += float(loss)
                epoch_metric += float(metric)

            loss_val = epoch_loss / n
            metric_val = epoch_metric / n
            self._update_history(loss_val, metric_val)
            self._log(epoch, loss_val, metric_val)

            if self.early_stopper and self.early_stopper(loss_val):
                if self.model.verbose:
                    print(f"Early stopping at epoch {epoch + 1}")
                break


class MiniBatchTrainer(BaseTrainer):
    """Mini‑batch gradient descent."""

    def run(self, X, Y):
        n = X.shape[0]
        bs = self.batch_size or 32
        for epoch in range(self.iterations):
            epoch_loss = epoch_metric = 0.0
            for start in range(0, n, bs):
                end = start + bs
                x_mb, y_mb = X[start:end], Y[start:end]
                with tf.GradientTape() as tape:
                    tape.watch(self.model.weights)
                    loss = self.model._cost_function(x_mb, y_mb)
                    metric = self.model._compute_metric(x_mb, y_mb)
                grads = tape.gradient(loss, [self.model.weights])
                if grads[0] is None:
                    grads[0] = tf.zeros_like(self.model.weights)
                self.optimizer.apply_gradients(zip(grads, [self.model.weights]))
                epoch_loss += float(loss) * x_mb.shape[0]
                epoch_metric += float(metric) * x_mb.shape[0]

            loss_val = epoch_loss / n
            metric_val = epoch_metric / n
            self._update_history(loss_val, metric_val)
            self._log(epoch, loss_val, metric_val)

            if self.early_stopper and self.early_stopper(loss_val):
                if self.model.verbose:
                    print(f" Early stopping at epoch {epoch + 1}")
                break


class MLETrainer(BaseTrainer):
    """Batch GD until the change in loss is smaller than *tol*."""

    def run(self, X, Y):
        prev = np.inf
        for epoch in range(self.iterations):
            with tf.GradientTape() as tape:
                tape.watch(self.model.weights)
                loss = self.model._cost_function(X, Y)
                metric = self.model._compute_metric(X, Y)
            grads = tape.gradient(loss, [self.model.weights])
            if grads[0] is None:
                grads[0] = tf.zeros_like(self.model.weights)
            self.optimizer.apply_gradients(zip(grads, [self.model.weights]))

            loss_val = float(loss)
            metric_val = float(metric)
            self._update_history(loss_val, metric_val)
            self._log(epoch, loss_val, metric_val)

            if abs(prev - loss_val) < self.tol:
                if self.model.verbose:
                    print(
                        f"Convergence reached after {epoch+1} iterations "
                        f"(Δloss={abs(prev-loss_val):.3e}) | "
                        f"{self.model.metric.capitalize()}={metric_val:.4f}"
                    )
                break
            prev = loss_val

            if self.early_stopper and self.early_stopper(loss_val):
                if self.model.verbose:
                    print(f"Early stopping at epoch {epoch + 1}")
                break


class LBFGSTrainer(BaseTrainer):
    """Limited‑memory BFGS optimiser via TensorFlow‑Probability."""

    def run(self, X, Y):
        if tfp is None:
            raise ImportError("LBFGS needs tensorflow‑probability")

        X64, Y64 = tf.cast(X, tf.float64), tf.cast(Y, tf.float64)
        w0 = tf.cast(self.model.weights, tf.float64)

        def loss_and_grad(w_flat):
            """Closure required by TFP’s optimiser (returns loss & grad)."""
            w = tf.reshape(w_flat, w0.shape)
            with tf.GradientTape() as tape:
                tape.watch(w)
                logits = tf.matmul(X64, w)
                preds = tf.nn.softmax(logits)
                loss_val = tf.reduce_mean(
                    tf.keras.losses.categorical_crossentropy(Y64, preds)
                )
            grad = tape.gradient(loss_val, w)
            return loss_val, tf.reshape(grad, [-1])

        res = tfp.optimizer.lbfgs_minimize(
            loss_and_grad,
            initial_position=tf.reshape(w0, [-1]),
            tolerance=self.tol,
            max_iterations=self.iterations,
        )

        new_w = tf.reshape(tf.cast(res.position, tf.float32), w0.shape)
        self.model.weights.assign(new_w)

        raw = self.model._compute_metric(X, Y)
        final_metric = float(raw.numpy()) if isinstance(raw, tf.Tensor) else float(raw)

        self._update_history(float(res.objective_value.numpy()), final_metric)
        if self.model.verbose:
            print(
                f"LBFGS finished in {res.num_iterations} iterations | "
                f"Loss={float(res.objective_value):.6f} | "
                f"{self.model.metric.capitalize()}={final_metric:.4f}"
            )


class NewtonTrainer(BaseTrainer):
    """Newton–Raphson / Iteratively Re‑weighted Least Squares (binary only)."""

    def run(self, X, Y):
        if self.model.num_classes not in (1, 2):
            raise ValueError("NewtonTrainer requires a **binary** problem.")

        Xn, y = X.numpy(), Y.numpy().ravel()
        w = (
            self.model.weights.numpy()
            if self.model.weights.shape[1] == 1
            else self.model.weights.numpy()[:, 1:2]
        )

        for epoch in range(self.iterations):
            z = Xn @ w
            p = 1 / (1 + np.exp(-z))
            r = (p * (1 - p)).ravel()
            H = Xn.T @ (r[:, None] * Xn) + 1e-6 * np.eye(self.model.n_features)
            g = Xn.T @ (y.reshape(-1, 1) - p)

            delta = np.linalg.solve(H, g)
            w += delta

            self.model.weights.assign(w.astype(np.float32))

            raw = self.model._compute_metric(X, Y)
            metric_val = float(raw.numpy()) if isinstance(raw, tf.Tensor) else float(raw)
            loss_val = float(self.model._cost_function(X, Y).numpy())

            self._update_history(loss_val, metric_val)
            self._log(epoch, loss_val, metric_val)

            if np.linalg.norm(delta) < self.tol:
                if self.model.verbose:
                    print(
                        f"Convergence reached after {epoch+1} iterations "
                        f"(||Δw||={np.linalg.norm(delta):.3e}) | "
                        f"{self.model.metric.capitalize()}={metric_val:.4f}"
                    )
                break

            if self.early_stopper and self.early_stopper(loss_val):
                if self.model.verbose:
                    print(f"⏹ Early‑stopping at epoch {epoch + 1}")
                break


# Factory helper
TRAINER_MAP: Dict[str, Type[BaseTrainer]] = {
    "batch": BatchTrainer,
    "stochastic": StochasticTrainer,
    "mini-batch": MiniBatchTrainer,
    "mle": MLETrainer,
    "lbfgs": LBFGSTrainer,
    "newton": NewtonTrainer,
}


def build_trainer(
    *,
    method: str,
    model,
    optimizer: tf.optimizers.Optimizer,
    iterations: int,
    batch_size: int | None = None,
    tol: float = 1e-6,
    early_stopper: Optional[Callable[[float], bool]] = None,
) -> BaseTrainer:
    """Return an initialised trainer matching *method*.

    Args
    ----
    method:
        Key of the desired strategy (see :pydata:`TRAINER_MAP`).
    model:
        The parent :class:`~mlektic.logistic_reg.LogisticRegressionArcht`.
    optimizer:
        Optimiser instance to be forwarded to the trainer.
    iterations:
        Maximum number of iterations/epochs.
    batch_size:
        Mini‑batch size (only meaningful for the mini‑batch strategy).
    tol:
        Numerical tolerance for iterative convergence criteria.
    early_stopper:
        Callback implementing the patience/min_delta early‑stopping rule.

    Returns
    -------
    BaseTrainer
        A fully configured trainer ready to :pymeth:`BaseTrainer.run`.

    Raises
    ------
    ValueError
        If *method* is not one of the recognised keys.
    """
    if method not in TRAINER_MAP:
        raise ValueError(
            f"Unsupported training method '{method}'. "
            f"Available: {list(TRAINER_MAP.keys())}"
        )
    cls = TRAINER_MAP[method]
    return cls(
        model=model,
        optimizer=optimizer,
        iterations=iterations,
        batch_size=batch_size,
        tol=tol,
        early_stopper=early_stopper,
    )
