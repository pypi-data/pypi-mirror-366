# mlektic/reporting/collector.py
from collections.abc import Sequence
import importlib.metadata as _meta
from datetime import datetime
from random import sample
import base64, io, sys, platform, psutil, torch
import numpy as np, pandas as pd, matplotlib.pyplot as plt
import matplotlib as mpl

from .utils import nice_model_name, fmt_datetime, fmt_duration, fmt_float

_MPL_BACKEND = "Agg"
plt.switch_backend(_MPL_BACKEND)

plt.style.use("seaborn-v0_8-dark-palette")
mpl.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "mathtext.fontset": "cm",
    "axes.titleweight": "bold",
})

class ExperimentCollector:
    """Extrae TODA la información necesaria para el reporte."""

    @staticmethod
    def _fig_to_b64(fig) -> str:
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        return base64.b64encode(buf.getvalue()).decode("ascii")

    # [i18n] —— descripción de objetos (optimizador / regularizador)
    @staticmethod
    def _describe_obj(obj, *, only_defaults: bool = False, dec: int = 4, language: str = "es") -> str:
        if obj is None:
            return "Ninguna" if (language or "es").lower() == "es" else "None"

        if hasattr(obj, "_reg_meta"):
            m = obj._reg_meta
            lam = f"\\({float(m['lambda']):.{dec}f}\\)"
            if m["method"] == "elastic_net":
                a = f"\\({float(m['alpha']):.{dec}f}\\)"
                return f"{m['method']} (λ={lam}, α={a})"
            return f"{m['method']} (λ={lam})"

        name = getattr(obj, "__class__", type(obj)).__name__
        params = {}
        try:
            if only_defaults and hasattr(obj, "defaults"):
                params = obj.defaults
            else:
                params = {k: v for k, v in vars(obj).items() if not k.startswith("_")}
        except Exception:
            params = {}

        if not params:
            return name

        def _fmt(v):
            try:
                return f"\\({float(v)}\\)"
            except Exception:
                return str(v)

        pars = ", ".join(f"{k}={_fmt(v)}" for k, v in params.items())
        return f"{name}({pars})"

    # [i18n] —— nombres de métricas por idioma
    @staticmethod
    def _metric_display(name: str, language: str = "es") -> str:
        n = name.lower()
        if (language or "es").lower() == "en":
            mapping = {
                "accuracy": "Accuracy",
                "precision": "Precision",
                "recall": "Recall",
                "f1_score": "F1 Score",
                "binary_crossentropy": "Binary cross-entropy",
                "categorical_crossentropy": "Categorical cross-entropy",
                "mse": "MSE",
                "rmse": "RMSE",
                "mae": "MAE",
                "r2": "R2",
            }
            return mapping.get(n, n.replace("_", " ").capitalize())
        else:
            mapping = {
                "accuracy": "Exactitud (Accuracy)",
                "precision": "Precisión (Precision)",
                "recall": "Sensibilidad (Recall)",
                "f1_score": "Puntaje F1 (F1_Score)",
                "binary_crossentropy": "Entropía cruzada binaria",
                "categorical_crossentropy": "Entropía cruzada categórica",
                "mse": "MSE",
                "rmse": "RMSE",
                "mae": "MAE",
                "r2": "R2",
            }
            return mapping.get(n, n.replace("_", " ").capitalize())

    @staticmethod
    def _build_results_section(
        model,
        is_classif: bool,
        y_train_arr: np.ndarray,
        X_train, y_train,
        X_val,   y_val,
        X_test,  y_test,
        dec: int,
        class_names: list[str] | None = None,
        *, language: str = "es",   # [i18n] ← nuevo
    ) -> dict:
        def _safe_eval(mtr, X, y):
            if X is None or y is None:
                return None
            try:
                return float(model.eval((X, y), mtr))
            except Exception:
                try:
                    return float(model.eval((X, y)))
                except Exception:
                    return None

        if is_classif:
            num_cls = getattr(model, "num_classes", len(np.unique(y_train_arr)))
            base = ["accuracy", "precision", "recall", "f1_score"]
            base += (["binary_crossentropy"] if num_cls == 2 else ["categorical_crossentropy"])
        else:
            base = ["mse", "rmse", "mae", "r2"]

        metrics_tbl = []
        for m in base:
            tr = _safe_eval(m, X_train, y_train)
            vl = _safe_eval(m, X_val,   y_val)
            te = _safe_eval(m, X_test,  y_test)
            if tr is vl is te is None:
                continue
            metrics_tbl.append(dict(
                name  = ExperimentCollector._metric_display(m, language),
                train = fmt_float(tr, dec) if tr is not None else "—",
                val   = fmt_float(vl, dec) if vl is not None else "—",
                test  = fmt_float(te, dec) if te is not None else "—",
            ))

        out = dict(metrics_table=metrics_tbl)

        # ── Matriz de confusión (etiquetas por idioma)
        if is_classif and hasattr(model, "eval"):
            try:
                cm = (model.eval((X_test, y_test), "confusion_matrix", to_df=True)
                      if X_test is not None else None)
                if hasattr(cm, "to_html"):
                    import pandas as pd
                    df = cm.copy() if isinstance(cm, pd.DataFrame) else None

                    if df is not None:
                        # Traducción de textos fijos TP/FP/FN/TN SOLO en español
                        if (language or "es").lower() == "es":
                            def _tr(v):
                                if isinstance(v, str):
                                    v = v.replace("True Positives (TP)",  "Verdaderos positivos (VP)")
                                    v = v.replace("False Positives (FP)", "Falsos positivos (FP)")
                                    v = v.replace("True Negatives (TN)",  "Verdaderos negativos (VN)")
                                    v = v.replace("False Negatives (FN)", "Falsos negativos (FN)")
                                return v
                            try:
                                df = df.map(_tr)
                            except AttributeError:
                                df = df.apply(lambda s: s.map(_tr))

                        # Encabezados/filas 2x2 o multicase
                        if df.shape == (2, 2):
                            pos = neg = None
                            try:
                                idx2lab = getattr(model, "_class_index_to_label", None)
                                if isinstance(idx2lab, dict):
                                    neg = str(idx2lab.get(0, None))
                                    pos = str(idx2lab.get(1, None))
                            except Exception:
                                pass
                            if (pos is None or neg is None) and class_names and len(class_names) >= 2:
                                cn = [str(c).strip() for c in class_names]
                                if set(map(str.lower, cn)) == {"0", "1"}:
                                    if (language or "es").lower() == "es":
                                        neg, pos = "No", "Sí"
                                    else:
                                        neg, pos = "No", "Yes"
                                else:
                                    neg, pos = cn[0], cn[1]

                            pos = pos or ("Sí" if (language or "es").lower() == "es" else "Yes")
                            neg = neg or "No"

                            if (language or "es").lower() == "es":
                                df.index   = [f"Predicción positiva ({pos})",
                                              f"Predicción negativa ({neg})"]
                                df.columns = [f"Real positiva ({pos})",
                                              f"Real negativa ({neg})"]
                            else:
                                df.index   = [f"Predicted positive ({pos})",
                                              f"Predicted negative ({neg})"]
                                df.columns = [f"Actual positive ({pos})",
                                              f"Actual negative ({neg})"]
                        else:
                            if class_names and len(class_names) == df.shape[0]:
                                if (language or "es").lower() == "es":
                                    df.index   = [f"Predicción {c}" for c in class_names]
                                    df.columns = [f"Real {c}"       for c in class_names]
                                else:
                                    df.index   = [f"Predicted {c}" for c in class_names]
                                    df.columns = [f"Actual {c}"    for c in class_names]
                            else:
                                if (language or "es").lower() == "es":
                                    df.index   = [str(ix).replace("Predicted ", "Predicción ")
                                                  for ix in df.index]
                                    df.columns = [str(c).replace("Actual ", "Real ")
                                                          .replace("Predicted ", "Predicción ")
                                                  for c in df.columns]
                                # en inglés no se reemplaza (ya viene en EN)

                        out["confusion_matrix"] = df.to_html(classes="table table-sm text-center cm-table")
                    else:
                        html = cm.to_html(classes="table table-sm text-center cm-table")
                        if (language or "es").lower() == "es":
                            html = (html.replace("True Positives (TP)",  "Verdaderos positivos (VP)")
                                        .replace("False Positives (FP)", "Falsos positivos (FP)")
                                        .replace("True Negatives (TN)",  "Verdaderos negativos (VN)")
                                        .replace("False Negatives (FN)", "Falsos negativos (FN)")
                                        .replace("Predicted ", "Predicción ")
                                        .replace("Actual ",    "Real "))
                        out["confusion_matrix"] = html
            except Exception:
                pass

        return out

    @staticmethod
    def _param_sample_and_eq(
        model,
        y_train,
        dec: int,
        *,
        max_params: int = 10,
        language: str = "es",     # [i18n] ← nuevo
    ) -> tuple[list[tuple[str,str,str,str]], str]:
        import numpy as _np

        ph_table: list[tuple[str,str,str,str]] = []

        def _fmt_num(x: float, d: int = dec) -> str:
            try:
                s = f"{float(x):.{d}f}".rstrip("0").rstrip(".")
                return "0" if s in {"-0", "-0."} else s
            except Exception:
                return str(x)

        def _latex_bmatrix(mat: _np.ndarray) -> str:
            rows = [" & ".join(_fmt_num(v) for v in row) for row in mat]
            return "\\begin{bmatrix}\n" + " \\\\\n".join(rows) + "\n\\end{bmatrix}"

        def _latex_colvec(vec: _np.ndarray) -> str:
            v = vec.reshape(-1, 1)
            return _latex_bmatrix(v)

        def _latex_x_symbols(d: int) -> str:
            syms = [[f"x_{{{i+1}}}"] for i in range(d)]
            rows = [" & ".join(r) for r in syms]
            return "\\begin{bmatrix}\n" + " \\\\\n".join(rows) + "\n\\end{bmatrix}"

        w = getattr(model, "weights", None)
        if w is not None:
            w_end  = w.detach().cpu().numpy()
            snaps  = getattr(model, "_snapshots", {})
            w_start = snaps.get("start", w_end)
            w_mid   = snaps.get("mid",   w_end)
            flat    = w_end.ravel()

            from random import sample as _smpl
            k_req = int(max_params)
            k = int(max(0, min(k_req, 50)))
            k = min(k, len(flat))
            idxs = _smpl(range(len(flat)), k) if k > 0 else []

            def _latex_num_wrapped(v):
                try:
                    return f"\\({_fmt_num(v, dec)}\\)"
                except Exception:
                    return str(v)

            for ix in idxs:
                coord = _np.unravel_index(ix, w_end.shape)
                coord_str = ",".join(map(str, coord))
                name_ltx  = f"\\(\\theta_{{{coord_str}}}\\)"
                ph_table.append((
                    name_ltx,
                    _latex_num_wrapped(w_start.ravel()[ix]),
                    _latex_num_wrapped(w_mid.ravel()[ix]),
                    _latex_num_wrapped(flat[ix]),
                ))

        eq_parts: list[str] = []

        coefs = None
        bias  = None
        if hasattr(model, "get_parameters"):
            try: coefs = model.get_parameters()
            except Exception: coefs = None
        if hasattr(model, "get_intercept"):
            try: bias = model.get_intercept()
            except Exception: bias = None

        d = K = None
        if coefs is not None:
            d = int(coefs.shape[0])
            K = int(coefs.shape[1]) if coefs.ndim == 2 else 1
        elif w is not None:
            W_full = w.detach().cpu().numpy()
            if getattr(model, "use_intercept", False) and W_full.shape[0] >= 2:
                d = int(W_full.shape[0] - 1)
            else:
                d = int(W_full.shape[0])
            K = int(W_full.ndim == 2 and W_full.shape[1] or 1)

        if d is None or K is None:
            return ph_table, ""

        if coefs is None and w is not None:
            W_full = w.detach().cpu().numpy()
            if getattr(model, "use_intercept", False) and W_full.shape[0] >= 2:
                coefs = W_full[1:, :] if W_full.ndim == 2 else W_full[1:, None]
                bias  = (W_full[0, :].ravel() if W_full.ndim == 2 else float(W_full[0]))
            else:
                coefs = W_full if W_full.ndim == 2 else W_full.reshape(-1, 1)
                bias  = None

        if coefs is not None and coefs.ndim == 1:
            coefs = coefs.reshape(-1, 1)
        if K == 1 and isinstance(bias, _np.ndarray) and bias.size == 1:
            bias = float(bias.ravel()[0])

        name_lc = type(model).__name__.lower()
        is_logistic = "logistic" in name_lc
        is_linear   = ("linear" in name_lc) and not is_logistic

        # [i18n] —— glosas explicativas
        if is_logistic:
            if K == 1:
                cflat = coefs.reshape(-1)
                terms = [f"{_fmt_num(c)}\\,x_{{{i+1}}}" for i, c in enumerate(cflat)]
                linear = " + ".join(terms) + (f" + {_fmt_num(bias, dec)}" if bias is not None else "")

                eq_parts.append("\\[ \\hat{p} = \\sigma(t),\\quad \\hat{y} = \\mathbb{1}[\\hat{p} \\ge 0.5], \\]")
                eq_parts.append("\\[ t = " + linear + ", \\]")
                eq_parts.append("\\[ \\sigma(t) = \\frac{1}{1 + e^{-t}}, \\]")
                if (language or "es").lower() == "es":
                    eq_parts.append(
                        "<p class='text-muted small'>"
                        "donde \\(t\\) es la combinación lineal escalar de las variables de entrada; "
                        "\\(\\hat{p}\\) es la probabilidad estimada de la clase positiva y "
                        "\\(\\hat{y}\\) es la clase predicha (1 si \\(\\hat{p}\\ge 0.5\\), 0 en caso contrario)."
                        "</p>"
                    )
                else:
                    eq_parts.append(
                        "<p class='text-muted small'>"
                        "where \\(t\\) is the scalar linear combination of input variables; "
                        "\\(\\hat{p}\\) is the estimated probability of the positive class, and "
                        "\\(\\hat{y}\\) is the predicted class (1 if \\(\\hat{p}\\ge 0.5\\), 0 otherwise)."
                        "</p>"
                    )
            else:
                eq_parts.append(
                    "\\[ \\hat{\\mathbf{p}} = \\mathrm{softmax}(W^{\\top}\\,\\mathbf{x} + \\mathbf{b}),"
                    "\\quad \\hat{y} = \\arg\\max_k \\hat{\\mathbf{p}}_k \\]"
                )
                eq_parts.append(
                    f"\\[ W \\in \\mathbb{{R}}^{{{d}\\times {K}}},\\ "
                    f"W^{{\\top}} \\in \\mathbb{{R}}^{{{K}\\times {d}}},\\ "
                    f"\\mathbf{{x}} \\in \\mathbb{{R}}^{{{d}}},\\ "
                    f"\\mathbf{{b}} \\in \\mathbb{{R}}^{{{K}}} \\]"
                )
                eq_parts.append("\\[ W = " + _latex_bmatrix(coefs) + " \\]")
                eq_parts.append("\\[ \\mathbf{x} = " + _latex_x_symbols(d) + " \\]")
                if bias is not None:
                    b_vec = _np.array(bias).reshape(-1)
                    eq_parts.append("\\[ \\mathbf{b} = " + _latex_colvec(b_vec) + " \\]")
                eq_parts.append(
                    "\\[ \\mathrm{softmax}(\\mathbf{t})_k \\,=\\, "
                    "\\frac{e^{t_k}}{\\sum_{j=1}^{K} e^{t_j}}, \\]"
                )
                if (language or "es").lower() == "es":
                    eq_parts.append(
                        "<p class='text-muted small'>"
                        "donde \\(\\mathbf{t} = W^{\\top}\\mathbf{x} + \\mathbf{b} \\in \\mathbb{R}^K\\) "
                        "son los <em>logits</em> por clase; \\(k\\) es el índice de clase "
                        "con \\(k\\in\\{1,\\dots,K\\}\\) y \\(K\\) es el número de clases. "
                        "El vector \\(\\hat{\\mathbf{p}}\\) contiene las probabilidades por clase y "
                        "\\(\\hat{y}\\) es la clase con mayor probabilidad calculada para el dato de entrada."
                        "</p>"
                    )
                else:
                    eq_parts.append(
                        "<p class='text-muted small'>"
                        "where \\(\\mathbf{t} = W^{\\top}\\mathbf{x} + \\mathbf{b} \\in \\mathbb{R}^K\\) "
                        "are the per-class logits; \\(k\\) is the class index "
                        "with \\(k\\in\\{1,\\dots,K\\}\\) and \\(K\\) the number of classes. "
                        "The vector \\(\\hat{\\mathbf{p}}\\) holds class probabilities, and "
                        "\\(\\hat{y}\\) is the most probable class for the input."
                        "</p>"
                    )
        else:
            cflat = coefs.reshape(-1)
            terms = [f"{_fmt_num(c)}\\,x_{{{i+1}}}" for i, c in enumerate(cflat)]
            linear = " + ".join(terms) + (f" + {_fmt_num(bias, dec)}" if bias is not None else "")
            eq_parts.append("\\[ \\hat{y} = " + linear + ", \\]")
            if (language or "es").lower() == "es":
                eq_parts.append(
                    "<p class='text-muted small'>"
                    "donde \\(\\hat{y}\\) es la predicción de la variable continua objetivo. "
                    "El modelo es una combinación lineal de las variables de entrada \\(x_1,\\ldots,x_d\\) "
                    "con un término independiente \\(b\\) (si corresponde)."
                    "</p>"
                )
            else:
                eq_parts.append(
                    "<p class='text-muted small'>"
                    "where \\(\\hat{y}\\) is the prediction of the continuous target variable. "
                    "The model is a linear combination of inputs \\(x_1,\\ldots,x_d\\) "
                    "with an intercept term \\(b\\) (if present)."
                    "</p>"
                )

        eq = "\n".join(eq_parts)
        return ph_table, eq

    @classmethod
    def collect(
        cls, *, model, run_id: str,
        t_start: datetime | None, t_end: datetime | None,
        X_train, y_train, X_val=None, y_val=None, X_test=None, y_test=None,
        dataset_name: str | None, preprocessing: str | list[str] | None,
        class_names: list[str] | None, feature_names: list[str] | None,
        target_name: str | None, decimals_stats: int = 4, language: str = "es",
        software_section: bool = False, hardware_section: bool = False,
        preprocessing_note: str | None = None,
        params_sample_n: int = 10,
    ):
        lang = (language or "es").lower()

        def _pretty(txt: str) -> str:
            return txt.replace("_", " ").capitalize()

        torch_version   = torch.__version__
        mlektic_version = _meta.version("mlektic")

        exec_data = dict(
            model_name      = nice_model_name(type(model).__name__, language=lang),
            run_id          = run_id,
            start_time      = fmt_datetime(t_start),
            end_time        = fmt_datetime(t_end),
            duration        = fmt_duration(t_start, t_end),
            torch_version   = torch_version,
            mlektic_version = mlektic_version,
            python_version  = sys.version.split()[0],
            device       = "GPU" if torch.cuda.is_available() else "CPU",
            gpu_name     = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "—",
            ram_total    = f"{psutil.virtual_memory().total/1e9:.2f} GB",
            host         = platform.node(),
            os           = f"{platform.system()} {platform.release()}",
            seed         = torch.initial_seed() % 2**32,
        )

        # ---- nombres, dimensiones, etc. (sin cambios en la lógica)
        def infer_feature_names(X):
            if feature_names:
                return list(feature_names)
            for attr in ("_feature_names", "feature_names", "input_names", "inputs_names"):
                if hasattr(model, attr) and getattr(model, attr) is not None:
                    return list(getattr(model, attr))
            if hasattr(X, "_feature_names"):
                return list(getattr(X, "_feature_names"))
            if hasattr(X, "columns"):
                return list(X.columns)
            if hasattr(X, "shape") and len(X.shape) == 2:
                return [f"x{i+1}" for i in range(X.shape[1])]
            return []

        def infer_target_name(y):
            if target_name:
                return target_name
            for attr in ("_target_name", "target_name", "output_name"):
                if hasattr(model, attr) and getattr(model, attr) is not None:
                    return getattr(model, attr)
            if hasattr(y, "_target_name"):
                return getattr(y, "_target_name")
            if hasattr(y, "name") and y.name is not None:
                return y.name
            return "y"

        fnames = infer_feature_names(X_train)
        tname  = infer_target_name(y_train)

        n_train = len(X_train)
        n_val   = 0 if X_val  is None else len(X_val)
        n_test  = 0 if X_test is None else len(X_test)
        total   = max(n_train + n_val + n_test, 1)

        def _num_targets(*ys):
            y0 = next((yy for yy in ys if yy is not None), None)
            if y0 is None:
                return 0
            y_arr = np.asarray(y0)
            return 1 if y_arr.ndim == 1 else y_arr.shape[1]

        n_targets = _num_targets(y_train, y_val, y_test)

        if isinstance(preprocessing, str):
            preprocessing_list = None
            preprocessing_text = preprocessing
        elif isinstance(preprocessing, Sequence) and not isinstance(preprocessing, (str, bytes)) and preprocessing:
            preprocessing_list = list(preprocessing)
            preprocessing_text = None
        else:
            preprocessing_list = preprocessing_text = None

        ds = dict(
            name       = dataset_name or "N/A",
            dims       = f"{total}×{len(fnames) + n_targets}",
            target     = tname,
            features   = fnames,
            features_show = ", ".join(fnames[:50]) + (" …" if len(fnames) > 50 else ""),
            split      = dict(
                train = dict(n=n_train, pct=100*n_train/total),
                val   = dict(n=n_val,   pct=100*n_val/total),
                test  = dict(n=n_test,  pct=100*n_test/total),
            ),
            preprocessing_list = preprocessing_list,
            preprocessing_note = preprocessing_note,
            preprocessing_text = preprocessing_text,
        )

        y_arr = np.asarray(y_train) if not isinstance(y_train, np.ndarray) else y_train
        if y_arr.ndim > 1:
            y_arr = y_arr.ravel()

        figs = {}

        # Clasificación / Regresión
        if len(np.unique(y_arr)) <= 20 and y_arr.ndim == 1:
            labels_order = getattr(model, "_class_names", None)
            y_np = np.asarray(y_arr)
            ds_classes = {}
            if labels_order:
                if np.issubdtype(y_np.dtype, np.number):
                    for i, name in enumerate(labels_order):
                        ds_classes[str(name)] = int((y_np == i).sum())
                else:
                    for name in labels_order:
                        ds_classes[str(name)] = int((y_np == name).sum())
            else:
                vc = pd.Series(y_np).value_counts(sort=False)
                ds_classes = {str(k): int(v) for k, v in vc.items()}

            ds["classes"] = ds_classes

            # Pie (título por idioma)
            fig_pie = plt.figure(figsize=(4, 4))
            labels = list(ds_classes.keys())
            sizes  = list(ds_classes.values())

            def autopct_fmt(pct):
                return f"{pct:1.1f}%" if pct > 0 else ""

            wedges, texts, autotexts = plt.pie(
                sizes,
                labels=labels,
                autopct=autopct_fmt,
                startangle=90,
                textprops={"fontweight": "bold"},
            )
            for text in texts:
                text.set_fontweight("bold")
            for autotext in autotexts:
                autotext.set_fontweight("bold")
                autotext.set_color("white")

            plt.axis("equal")
            plt_title = "Distribución de clases" if lang == "es" else "Class distribution"
            plt.title(plt_title, fontweight="bold")

            figs["class_pie"] = cls._fig_to_b64(fig_pie)
            is_classif = True
        else:
            ds_classes = None
            is_classif = False

        # ===== Hiperparámetros =====
        def _latex_int_or_dash(val):
            if val is None or val == "—":
                return "—"
            try:
                return f"\\({int(val)}\\)"
            except Exception:
                return f"\\({val}\\)"

        def _fmt_trim(x, dec: int = 6) -> str:
            try:
                s = f"{float(x):.{dec}f}".rstrip("0").rstrip(".")
                return f"\\({s}\\)"
            except Exception:
                return str(x)

        def _infer_loss_name(model, is_classif: bool, y_arr: np.ndarray) -> str:
            name_lc = type(model).__name__.lower()
            if "logistic" in name_lc:
                numc = getattr(model, "num_classes", None)
                if numc is None:
                    try:
                        numc = len(np.unique(y_arr))
                    except Exception:
                        numc = 2
                if numc in (1, 2):
                    return "Entropía cruzada binaria" if lang == "es" else "Binary cross-entropy"
                return "Entropía cruzada categórica" if lang == "es" else "Categorical cross-entropy"
            if "linear" in name_lc:
                return "MSE"
            return ("Entropía cruzada binaria" if is_classif else "MSE") if lang == "es" else ("Binary cross-entropy" if is_classif else "MSE")

        epochs_val     = getattr(model, "iterations", None)
        batch_size_val = getattr(model, "batch_size", None)
        opt            = getattr(model, "opt", None)
        lr_val         = (getattr(opt, "defaults", {}) or {}).get("lr", None) if opt else None

        epochs_str   = _latex_int_or_dash(epochs_val) if epochs_val is not None else "—"
        batch_str    = _latex_int_or_dash(batch_size_val) if batch_size_val is not None else "—"
        lr_str       = _fmt_trim(lr_val, max(6, decimals_stats)) if lr_val is not None else "—"
        loss_name    = _infer_loss_name(model, is_classif, y_arr)

        regularizer_obj = getattr(model, "regularizer", None)
        reg_str = ("Sin regularización" if regularizer_obj is None else
                   ExperimentCollector._describe_obj(regularizer_obj, dec=decimals_stats, language=lang))
        if regularizer_obj is None and lang == "en":
            reg_str = "No regularization"

        # [i18n] — claves localizadas en la tabla de hiperparámetros
        if lang == "es":
            hp = {
                "Épocas":               epochs_str,
                "Tamaño de lote":       batch_str,
                "Tasa de aprendizaje":  lr_str,
                "Optimizador":          cls._describe_obj(getattr(model, "opt", None), only_defaults=True, dec=decimals_stats, language=lang) if hasattr(model, "opt") else "—",
                "Función de pérdida":   loss_name,
                "Regularización":       reg_str,
            }
        else:
            hp = {
                "Epochs":               epochs_str,
                "Batch size":           batch_str,
                "Learning rate":        lr_str,
                "Optimizer":            cls._describe_obj(getattr(model, "opt", None), only_defaults=True, dec=decimals_stats, language=lang) if hasattr(model, "opt") else "—",
                "Loss function":        loss_name,
                "Regularization":       reg_str,
            }

        def _num_plain(v):
            try:
                return f"{float(v):.{decimals_stats}f}"
            except Exception:
                return str(v)

        es = getattr(model, "_early", None)
        if es is None:
            hp["Detención temprana" if lang == "es" else "Early stopping"] = \
                ("Sin detención temprana" if lang == "es" else "No early stopping")
        else:
            pac_val = _num_plain(getattr(es, 'patience', '?'))
            md_val  = _num_plain(getattr(es, 'min_delta', '?'))
            if lang == "es":
                pac_str   = f"paciencia = \\({pac_val}\\)"
                delta_str = f"\\(\\delta_{{\\min}}\\) = \\({md_val}\\)"
                epo_str   = f"época = {_latex_int_or_dash(getattr(model, '_early_stop_epoch', None))}"
                hp["Detención temprana"] = f"{pac_str}, {delta_str}, {epo_str}"
            else:
                pac_str   = f"patience = \\({pac_val}\\)"
                delta_str = f"\\(\\delta_{{\\min}}\\) = \\({md_val}\\)"
                epo_str   = f"epoch = {_latex_int_or_dash(getattr(model, '_early_stop_epoch', None))}"
                hp["Early stopping"] = f"{pac_str}, {delta_str}, {epo_str}"

        loss_hist   = list(getattr(model, "cost_history", []))
        main_mtr    = getattr(model, "metric", "").lower()
        metric_hist = list(getattr(model, "metric_history", []))
        spec_hist   = list(getattr(model, f"{main_mtr}_history", []))
        acc_hist = (list(getattr(model, "accuracy_history", [])) or
                    list(getattr(model, "acc_history",      [])))

        figs.setdefault("loss_curve", None)
        figs.setdefault("metric_curve", None)
        method_name   = str(getattr(model, "method", "")).lower()
        hide_evolution = (method_name == "least_squares")

        metric_series: list[float] | None = None
        metric_label  : str               = ""

        if not hide_evolution:
            if len(np.unique(np.asarray(y_train))) <= 20:
                if spec_hist:
                    metric_series = spec_hist
                    metric_label  = _pretty(main_mtr)
                elif acc_hist:
                    metric_series = acc_hist
                    metric_label  = "Accuracy" if lang == "en" else "Accuracy"
                else:
                    try:
                        final_acc = float(model.eval((X_train, y_train), "accuracy"))
                        n_pts = len(loss_hist) or len(metric_hist) or 1
                        metric_series = [final_acc] * n_pts
                        metric_label  = "Accuracy"
                    except Exception:
                        pass
            else:
                if spec_hist:
                    metric_series = spec_hist
                    metric_label  = _pretty(main_mtr)
                else:
                    metric_label = "R2" if main_mtr == "mse" else _pretty(main_mtr)

                    if main_mtr == "mse" and loss_hist:
                        try:
                            var_y = float(np.var(np.asarray(y_train, dtype=float)))
                            if var_y > 0:
                                metric_series = [1 - (l / var_y) for l in loss_hist]
                        except Exception:
                            pass
                    if metric_series is None and metric_hist:
                        metric_series = metric_hist

        if (not hide_evolution) and loss_hist and len(loss_hist) > 1:
            fig1 = plt.figure()
            plt.plot(np.arange(1, len(loss_hist) + 1), loss_hist)
            plt.title("Pérdida vs Época" if lang == "es" else "Loss vs Epoch", fontweight="bold")
            plt.xlabel("Época" if lang == "es" else "Epoch", fontweight="bold")
            plt.ylabel("Pérdida" if lang == "es" else "Loss", fontweight="bold")
            figs["loss_curve"] = cls._fig_to_b64(fig1)

        if (not hide_evolution) and metric_series:
            fig2 = plt.figure()
            plt.plot(np.arange(1, len(metric_series) + 1), metric_series)
            plt.title(f"{metric_label} vs " + ("Época" if lang == "es" else "Epoch"), fontweight="bold")
            plt.xlabel("Época" if lang == "es" else "Epoch", fontweight="bold")
            plt.ylabel(metric_label, fontweight="bold")
            figs["metric_curve"] = cls._fig_to_b64(fig2)

        ph_table, eq = cls._param_sample_and_eq(
            model, y_train, decimals_stats, max_params=params_sample_n, language=lang
        )

        results = cls._build_results_section(
            model, is_classif, y_arr,
            X_train, y_train, X_val, y_val, X_test, y_test,
            decimals_stats,
            class_names=list(ds.get("classes", {}).keys()) if ds.get("classes") else None,
            language=lang,
        )

        return dict(
            exec              = exec_data,
            dataset           = ds,
            hparams           = hp,
            figs              = figs,
            results           = results,
            params_sample     = ph_table,
            equation          = eq,
            language          = language,
            software_section  = software_section,
            hardware_section  = hardware_section,
        )
