#mlektic\methods\optimizer_archt.py
from typing import Tuple

def optimizer_archt(
    method: str = "sgd-standard",
    learning_rate: float = 0.01,
    momentum: float = 0.0,
    nesterov: bool = False,
    batch_size: int = 32,
    *,
    backend: str = "torch",
) -> Tuple[object, str, int | None]:
    backend = backend.lower()
    if backend == "torch":
        import torch.optim as O

        if method == "sgd-standard":
            return (lambda p: O.SGD(p, lr=learning_rate), "batch", None)
        elif method == "sgd-stochastic":
            return (lambda p: O.SGD(p, lr=learning_rate), "stochastic", None)
        elif method == "sgd-mini-batch":
            return (lambda p: O.SGD(p, lr=learning_rate), "mini-batch", batch_size)
        elif method == "sgd-momentum":
            return (lambda p: O.SGD(p, lr=learning_rate, momentum=momentum), "batch", None)
        elif method == "nesterov":
            return (
                lambda p: O.SGD(p, lr=learning_rate, momentum=momentum, nesterov=True),
                "batch",
                None,
            )
        elif method == "adagrad":
            return (lambda p: O.Adagrad(p, lr=learning_rate), "batch", None)
        elif method == "adadelta":
            return (lambda p: O.Adadelta(p, lr=learning_rate), "batch", None)
        elif method == "rmsprop":
            return (lambda p: O.RMSprop(p, lr=learning_rate, momentum=momentum), "batch", None)
        elif method == "adam":
            return (lambda p: O.Adam(p, lr=learning_rate), "batch", None)
        elif method == "adamax":
            return (lambda p: O.Adamax(p, lr=learning_rate), "batch", None)
        elif method == "nadam":
            return (lambda p: O.NAdam(p, lr=learning_rate, momentum=momentum), "batch", None)

    elif backend == "tf":
        import tensorflow as _tf  # type: ignore

        if method == "sgd-standard":
            return (_tf.optimizers.SGD(learning_rate=learning_rate), "batch", None)
        elif method == "sgd-stochastic":
            return (_tf.optimizers.SGD(learning_rate=learning_rate), "stochastic", None)
        elif method == "sgd-mini-batch":
            return (_tf.optimizers.SGD(learning_rate=learning_rate), "mini-batch", batch_size)
        elif method == "sgd-momentum":
            return (
                _tf.optimizers.SGD(learning_rate=learning_rate, momentum=momentum),
                "batch",
                None,
            )
        elif method == "nesterov":
            return (
                _tf.optimizers.SGD(
                    learning_rate=learning_rate, momentum=momentum, nesterov=True
                ),
                "batch",
                None,
            )
        elif method == "adagrad":
            return (_tf.optimizers.Adagrad(learning_rate=learning_rate), "batch", None)
        elif method == "adadelta":
            return (_tf.optimizers.Adadelta(learning_rate=learning_rate), "batch", None)
        elif method == "rmsprop":
            return (_tf.optimizers.RMSprop(learning_rate=learning_rate), "batch", None)
        elif method == "adam":
            return (_tf.optimizers.Adam(learning_rate=learning_rate), "batch", None)
        elif method == "adamax":
            return (_tf.optimizers.Adamax(learning_rate=learning_rate), "batch", None)
        elif method == "nadam":
            return (_tf.optimizers.Nadam(learning_rate=learning_rate), "batch", None)


    raise ValueError(f"{method} is not a valid optimizer for backend '{backend}'.")
