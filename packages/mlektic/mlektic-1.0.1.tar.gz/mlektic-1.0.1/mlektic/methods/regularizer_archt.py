def regularizer_archt(
    method: str = "l1",
    lambda_value: float = 0.1,
    alpha: float = 0.5,
    *,
    backend: str = "torch",
):
    """
    Devuelve la callable de regularización y añade un atributo `_reg_meta`
    para que el reporter pueda identificar el método y sus parámetros.
    """
    backend = backend.lower()
    meta = {"method": method, "lambda": lambda_value, "alpha": alpha}

    if backend == "torch":
        import torch
        if method == "l1":
            fn = lambda w: lambda_value * torch.abs(w).sum()
        elif method == "l2":
            fn = lambda w: lambda_value * torch.square(w).sum()
        elif method == "elastic_net":
            fn = lambda w: lambda_value * (
                alpha * torch.abs(w).sum() + (1 - alpha) * torch.square(w).sum()
            )
        else:
            raise ValueError(f"{method} is not a valid value for regularizer (backend='{backend}').")

    elif backend == "tf":
        import tensorflow as tf  # type: ignore
        if method == "l1":
            fn = lambda w: lambda_value * tf.reduce_sum(tf.abs(w), axis=0)
        elif method == "l2":
            fn = lambda w: lambda_value * tf.reduce_sum(tf.square(w), axis=0)
        elif method == "elastic_net":
            fn = lambda w: lambda_value * (
                alpha * tf.reduce_sum(tf.abs(w), axis=0)
                + (1 - alpha) * tf.reduce_sum(tf.square(w), axis=0)
            )
        else:
            raise ValueError(f"{method} is not a valid value for regularizer (backend='{backend}').")
    else:
        raise ValueError(f"{backend} is not a supported backend for regularizer.")

    setattr(fn, "_reg_meta", meta)  # <- aquí guardamos los metadatos
    return fn
