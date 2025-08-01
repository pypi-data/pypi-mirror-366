#mlektic\methods\logreg_trainers_torch.py
"""
Entrenadores PyTorch para LogisticRegressionArchtImpl.
"""

from __future__ import annotations
import abc, torch
from typing import Callable, Optional

class BaseTrainer(abc.ABC):
    def __init__(
        self, *, model, optimizer: torch.optim.Optimizer,
        iterations: int, batch_size: int | None = None,
        tol: float = 1e-6, early_stopper: Optional[Callable[[float], bool]] = None,
    ):
        self.model, self.opt = model, optimizer
        self.iters, self.bs  = iterations, batch_size
        self.tol, self.stop  = tol, early_stopper

        # snapshots
        if not hasattr(self.model, "_snapshots"):
            self.model._snapshots = {}

    def _update(self, loss, metric, epoch):
        self.model.cost_history.append(loss)
        self.model.metric_history.append(metric)
        if epoch == 0:
            self.model._snapshots["start"] = self.model.weights.detach().cpu().clone().numpy()
        if epoch == max(self.iters // 2 - 1, 0):
            self.model._snapshots["mid"]   = self.model.weights.detach().cpu().clone().numpy()

    def _final(self):
        self.model._snapshots["end"] = self.model.weights.detach().cpu().clone().numpy()

    def _log(self, e, loss, metric):
        if self.model.verbose and (e+1) % max(1, self.iters//10) == 0:
            print(f"Epoch {e+1:>4d} | Loss={loss:.6f} | {self.model.metric.capitalize()}={metric:.4f}")

    @abc.abstractmethod
    def run(self, X: torch.Tensor, y: torch.Tensor): ...

# ------------------------------------------------------------------
class BatchTrainer(BaseTrainer):
    def run(self, X, y):
        for e in range(self.iters):
            self.opt.zero_grad()
            loss = self.model._loss(X, y); loss.backward(); self.opt.step()
            metric = float(self.model._metric_val(X, y))
            loss   = float(loss)
            self._update(loss, metric, e)
            self._log(e, loss, metric)
            if self.stop and self.stop(loss):
                self.model._early_stop_epoch = e+1
                if self.model.verbose: print(f"⏹ Early stop at epoch {e+1}")
                break
        self._final()

class StochasticTrainer(BaseTrainer):
    def run(self, X, y):
        n = len(X)
        for e in range(self.iters):
            perm = torch.randperm(n)
            for i in perm:
                xb, yb = X[i:i+1], y[i:i+1]
                self.opt.zero_grad(); loss = self.model._loss(xb, yb); loss.backward(); self.opt.step()
            loss_e = float(self.model._loss(X, y))
            metric = float(self.model._metric_val(X, y))
            self._update(loss_e, metric, e); self._log(e, loss_e, metric)
            if self.stop and self.stop(loss_e):
                self.model._early_stop_epoch = e+1
                if self.model.verbose: print(f"⏹ Early stop at epoch {e+1}")
                break
        self._final()

class MiniBatchTrainer(BaseTrainer):
    def run(self, X, y):
        n, bs = len(X), self.bs or 32
        for e in range(self.iters):
            perm = torch.randperm(n)
            for i in range(0, n, bs):
                idx = perm[i:i+bs]
                self.opt.zero_grad()
                loss = self.model._loss(X[idx], y[idx]); loss.backward(); self.opt.step()
            loss_e = float(self.model._loss(X, y))
            metric = float(self.model._metric_val(X, y))
            self._update(loss_e, metric, e); self._log(e, loss_e, metric)
            if self.stop and self.stop(loss_e):
                self.model._early_stop_epoch = e+1
                if self.model.verbose: print(f"⏹ Early stop at epoch {e+1}")
                break
        self._final()

class MLETrainer(BaseTrainer):
    """Full‑batch GD con criterio |Δloss|<tol."""
    def run(self, X, y):
        prev = float("inf")
        for e in range(self.iters):
            self.opt.zero_grad(); loss = self.model._loss(X, y); loss.backward(); self.opt.step()
            loss_e = float(loss)
            metric = float(self.model._metric_val(X, y))
            self._update(loss_e, metric, e); self._log(e, loss_e, metric)
            if abs(prev - loss_e) < self.tol:
                if self.model.verbose:
                    print(f"Convergió en la época {e+1} (Δloss={abs(prev-loss_e):.3e})")
                break
            prev = loss_e
            if self.stop and self.stop(loss_e):
                self.model._early_stop_epoch = e+1
                if self.model.verbose: print(f"⏹ Early stop at epoch {e+1}")
                break
        self._final()

TRAINERS = {
    "batch": BatchTrainer,
    "stochastic": StochasticTrainer,
    "mini-batch": MiniBatchTrainer,
    "mle": MLETrainer,
}

def build_trainer(
    *, method: str, model, optimizer, iterations: int,
    batch_size: int | None = None, tol: float = 1e-6,
    early_stopper: Optional[Callable[[float], bool]] = None,
):
    if method not in TRAINERS:
        raise ValueError(f"Método '{method}' no soportado (PyTorch logistic).")
    return TRAINERS[method](
        model=model, optimizer=optimizer, iterations=iterations,
        batch_size=batch_size, tol=tol, early_stopper=early_stopper,
    )
