# mlektic/methods/linreg_trainers_torch.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import abc, torch
from typing import Callable, Optional

class BaseTrainer(abc.ABC):
    def __init__(
        self,
        *,
        model,
        optimizer: torch.optim.Optimizer,
        iterations: int,
        batch_size: int | None = None,
        tol: float = 1e-6,
        early_stopper: Optional[Callable[[float], bool]] = None,
    ):
        self.model        = model
        self.optimizer    = optimizer
        self.iterations   = iterations
        self.batch_size   = batch_size
        self.tol          = tol
        self.early_stopper= early_stopper

        # para snapshots
        self._snapshots_enabled = True
        if not hasattr(self.model, "_snapshots"):
            self.model._snapshots = {}

    # helpers --------------------------------------------------------
    def _update_history(self, loss: float, metric: float, epoch: int):
        self.model.cost_history.append(loss)
        self.model.metric_history.append(metric)

        # snapshots
        if self._snapshots_enabled:
            if epoch == 0:
                self.model._snapshots["start"] = self.model.weights.detach().cpu().clone().numpy()
            if epoch == max(self.iterations // 2 - 1, 0):
                self.model._snapshots["mid"]   = self.model.weights.detach().cpu().clone().numpy()

    def _final_snapshot(self):
        if self._snapshots_enabled:
            self.model._snapshots["end"] = self.model.weights.detach().cpu().clone().numpy()

    def _log(self, e, loss, metric):
        if self.model.verbose and (e + 1) % max(1, self.iterations // 10) == 0:
            print(f"Epoch {e+1:>4d} | Loss={loss:.6f} | {self.model.metric.upper()}={metric:.4f}")

    @abc.abstractmethod
    def run(self, X: torch.Tensor, y: torch.Tensor) -> None:
        ...

# --------------------------- Trainers ---------------------------------
class BatchTrainer(BaseTrainer):
    def run(self, X, y):
        for epoch in range(self.iterations):
            self.optimizer.zero_grad()
            loss = self.model._loss(X, y); loss.backward(); self.optimizer.step()
            metric = self.model._metric_fn()(y, self.model._predict(X))
            loss, metric = float(loss), float(metric)

            self._update_history(loss, metric, epoch)
            self._log(epoch, loss, metric)

            if self.early_stopper and self.early_stopper(loss):
                self.model._early_stop_epoch = epoch + 1
                if self.model.verbose: print(f"⏹ Early stop at epoch {epoch+1}")
                break
        self._final_snapshot()

class StochasticTrainer(BaseTrainer):
    def run(self, X, y):
        n = len(X)
        for epoch in range(self.iterations):
            perm = torch.randperm(n)
            for i in perm:
                xb, yb = X[i:i+1], y[i:i+1]
                self.optimizer.zero_grad()
                loss = self.model._loss(xb, yb); loss.backward(); self.optimizer.step()
            loss_epoch = float(self.model._loss(X, y))
            metric     = float(self.model._metric_fn()(y, self.model._predict(X)))

            self._update_history(loss_epoch, metric, epoch)
            self._log(epoch, loss_epoch, metric)

            if self.early_stopper and self.early_stopper(loss_epoch):
                self.model._early_stop_epoch = epoch + 1
                if self.model.verbose: print(f"⏹ Early stop at epoch {epoch+1}")
                break
        self._final_snapshot()

class MiniBatchTrainer(BaseTrainer):
    def run(self, X, y):
        n, bs = len(X), self.batch_size or 32
        for epoch in range(self.iterations):
            perm = torch.randperm(n)
            for i in range(0, n, bs):
                idx = perm[i:i+bs]
                xb, yb = X[idx], y[idx]
                self.optimizer.zero_grad()
                loss = self.model._loss(xb, yb); loss.backward(); self.optimizer.step()
            loss_epoch = float(self.model._loss(X, y))
            metric     = float(self.model._metric_fn()(y, self.model._predict(X)))

            self._update_history(loss_epoch, metric, epoch)
            self._log(epoch, loss_epoch, metric)

            if self.early_stopper and self.early_stopper(loss_epoch):
                self.model._early_stop_epoch = epoch + 1
                if self.model.verbose: print(f"⏹ Early stop at epoch {epoch+1}")
                break
        self._final_snapshot()

class MLETrainer(BaseTrainer):
    """Full‑batch GD hasta que |Δloss|<tol."""
    def run(self, X, y):
        prev = float("inf")
        for epoch in range(self.iterations):
            self.optimizer.zero_grad()
            loss = self.model._loss(X, y); loss.backward(); self.optimizer.step()
            loss_val = float(loss)
            metric   = float(self.model._metric_fn()(y, self.model._predict(X)))

            self._update_history(loss_val, metric, epoch)
            self._log(epoch, loss_val, metric)

            if abs(prev - loss_val) < self.tol:
                if self.model.verbose:
                    print(f"Convergió en la época {epoch+1} (Δloss={abs(prev-loss_val):.3e})")
                break
            prev = loss_val
            if self.early_stopper and self.early_stopper(loss_val):
                self.model._early_stop_epoch = epoch + 1
                if self.model.verbose: print(f"⏹ Early stop at epoch {epoch+1}")
                break
        self._final_snapshot()

TRAINER_MAP = {
    "batch":       BatchTrainer,
    "stochastic":  StochasticTrainer,
    "mini-batch":  MiniBatchTrainer,
    "mle":         MLETrainer,
}

def build_trainer(
    *,
    method: str,
    model,
    optimizer: torch.optim.Optimizer,
    iterations: int,
    batch_size: int | None = None,
    tol: float = 1e-6,
    early_stopper: Optional[Callable[[float], bool]] = None,
) -> BaseTrainer:
    if method not in TRAINER_MAP:
        raise ValueError(f"Método '{method}' no soportado (PyTorch linear).")
    cls = TRAINER_MAP[method]
    return cls(
        model=model,
        optimizer=optimizer,
        iterations=iterations,
        batch_size=batch_size,
        tol=tol,
        early_stopper=early_stopper,
    )
