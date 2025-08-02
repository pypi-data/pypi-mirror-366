# mlektic/reporting/__init__.py
"""
API de más alto nivel — importa sólo esto:

>>> from mlektic.reporting import ReportBuilder
"""
from pathlib import Path
from .collector import ExperimentCollector
from .renderer  import HTMLRenderer

import re
import secrets
from datetime import datetime as _dt, timedelta
from functools import wraps

# ---------------------------------------------------------------------
# Utilidades de nombres
# ---------------------------------------------------------------------
def _infer_names(X, y, feature_names=None, target_name=None):
    """Función utilitaria para inferir nombres desde los datos."""
    # Feature names
    if feature_names is not None:
        fns = list(feature_names)
    elif hasattr(X, "columns"):  # pandas DataFrame
        fns = list(X.columns)
    elif hasattr(X, "_feature_names"):
        fns = list(getattr(X, "_feature_names"))
    else:
        if hasattr(X, "shape") and len(getattr(X, "shape", [])) == 2:
            fns = [f"x{i+1}" for i in range(X.shape[1])]
        else:
            fns = []

    # Target name
    if target_name is not None:
        tn = target_name
    elif hasattr(y, "name") and y.name is not None:
        tn = y.name
    elif hasattr(y, "_target_name"):
        tn = getattr(y, "_target_name")
    else:
        tn = "y"

    return fns, tn

_AUTO_RE = re.compile(r"x\d+$")

def _looks_auto(fns):
    """True si todos los nombres son del tipo x1, x2, ... (fallback)."""
    if not fns:
        return False
    return all(_AUTO_RE.fullmatch(str(n)) for n in fns)

def _slugify(s: str) -> str:
    """Minúsculas, sólo [a-z0-9_ -], espacios -> '_'."""
    s = s.lower()
    s = re.sub(r"[^a-z0-9_-]+", "_", s)
    s = re.sub(r"_{2,}", "_", s).strip("_")
    return s

def _auto_run_id(model) -> str:
    """
    Genera un identificador único de ejecución (run_id) con un
    prefijo corto y semántico.

    Prefijos asignados
    ------------------
    • linr → regresión lineal
    • logr → regresión logística
    • ann  → redes neuronales (TorchNN, Sequential, etc.)
    • <slug genérico> → cualquier otra clase

    El formato final es:
        <prefijo>-YYYYMMDD_HHMMSS-<hex>
    """
    name_lc = type(model).__name__.lower()

    if any(key in name_lc for key in ("linearregression", "linear_regression", "linearregarcht")):
        prefix = "linr"
    elif any(key in name_lc for key in ("logisticregression", "logistic_regression", "logisticregarcht")):
        prefix = "logr"
    elif any(key in name_lc for key in ("torchnn", "sequential", "ann", "nn")):
        prefix = "ann"
    else:
        prefix = _slugify(type(model).__name__)

    now = _dt.now()
    ts  = now.strftime("%Y%m%d_%H%M%S")
    rnd = secrets.token_hex(3)          # 6 caracteres hex

    return f"{prefix}-{ts}-{rnd}"
# ---------------------------------------------------------------------
# Hooks de tiempo (global por clase y local por instancia)
# ---------------------------------------------------------------------
_GLOBAL_TIMING_PATCHED = False

def _wrap_class_for_timing(cls):
    """
    Envuelve train/fit de UNA clase para registrar self._mlektic_t0/_mlektic_t1.
    Sólo se ejecuta una vez por clase.
    """
    if cls is None:
        return
    if getattr(cls, "_mlektic_time_hook_cls", False):
        return

    def _wrap_method(method_name: str):
        if not hasattr(cls, method_name):
            return
        original = getattr(cls, method_name)
        if not callable(original):
            return

        @wraps(original)
        def _timed(self, *args, **kwargs):
            self._mlektic_t0 = _dt.now()
            try:
                return original(self, *args, **kwargs)
            finally:
                self._mlektic_t1 = _dt.now()
        setattr(cls, method_name, _timed)

    _wrap_method("train")
    _wrap_method("fit")
    cls._mlektic_time_hook_cls = True

def _install_global_timing():
    """
    Parchea clases conocidas para medir tiempos aunque el builder se cree después.
    """
    global _GLOBAL_TIMING_PATCHED
    if _GLOBAL_TIMING_PATCHED:
        return

    try:
        from mlektic.linear_reg   import LinearRegressionArcht
    except Exception:
        LinearRegressionArcht = None
    try:
        from mlektic.logistic_reg import LogisticRegressionArcht
    except Exception:
        LogisticRegressionArcht = None
    try:
        from mlektic.nn.torch_impl import TorchNNArchtImpl
    except Exception:
        TorchNNArchtImpl = None

    for _cls in (LinearRegressionArcht, LogisticRegressionArcht, TorchNNArchtImpl):
        _wrap_class_for_timing(_cls)

    _GLOBAL_TIMING_PATCHED = True

# Ejecutar al importar el módulo
_install_global_timing()

def _install_time_hook(model):
    """
    Envuelve train/fit PARA ESTA INSTANCIA si aún no tiene hook.
    Si el modelo es custom y ya fue entrenado, no podremos recuperar
    el tiempo pasado, pero sí los próximos entrenos.
    """
    if getattr(model, "_mlektic_time_hook", False):
        return

    def _wrap(fn_name: str):
        if not hasattr(model, fn_name):
            return
        orig = getattr(model, fn_name)
        if not callable(orig):
            return

        @wraps(orig)
        def _timed(*args, **kwargs):
            model._mlektic_t0 = _dt.now()
            try:
                return orig(*args, **kwargs)
            finally:
                model._mlektic_t1 = _dt.now()
        setattr(model, fn_name, _timed)

    _wrap("train")
    _wrap("fit")
    model._mlektic_time_hook = True

def _pick_dt(model, *names):
    """Devuelve el primer atributo datetime válido que encuentre en model."""
    for n in names:
        v = getattr(model, n, None)
        if isinstance(v, _dt):
            return v
    return None

# ---------------------------------------------------------------------
# ReportBuilder
# ---------------------------------------------------------------------
class ReportBuilder:
    def __init__(self, *,
                    mdl,
                    run_id: str | None = None,
                    X_train=None, y_train=None,
                    X_val=None,   y_val=None,
                    X_test=None,  y_test=None,
                    dataset_name: str | None = None,
                    preprocessing: str | list[str] | None = None,
                    preprocessing_note: str | None = None,
                    class_names: list[str] | None = None,
                    feature_names: list[str] | None = None,
                    target_name: str | None = None,
                    decimals_stats: int = 4,
                    language: str = "es",
                    software_section: bool = False,
                    hardware_section: bool = False,
                    params_sample_n: int = 10):   # ← NUEVO parámetro (default 10)
        """
        Construye un reporte a partir de un modelo ya entrenado.

        Parámetros mínimos
        ------------------
        >>> ReportBuilder(mdl=my_model)

        Si `X_train`, `y_train`, etc. no se proporcionan, el Builder
        intentará recuperarlos del modelo mediante los atributos
        `_mlektic_X_train`, `_mlektic_y_train`, … que los back‑ends
        de mlektic guardan automáticamente al llamar `train()`.

        Otros parámetros (dataset_name, preprocessing, …) siguen
        siendo opcionales y sirven sólo para enriquecer el reporte.
        """
        # ------------------- modelo & run‑ID -------------------------
        self.model  = mdl
        self.run_id = run_id or _auto_run_id(mdl)

        # Hookear tiempos por si el modelo es custom
        _install_time_hook(self.model)

        # ------------------- recuperar datasets ---------------------
        def _fallback(attr, given):
            return given if given is not None else getattr(self.model, attr, None)

        self.X_train = _fallback("_mlektic_X_train", X_train)
        self.y_train = _fallback("_mlektic_y_train", y_train)
        self.X_val   = _fallback("_mlektic_X_val",   X_val)
        self.y_val   = _fallback("_mlektic_y_val",   y_val)
        self.X_test  = _fallback("_mlektic_X_test",  X_test)
        self.y_test  = _fallback("_mlektic_y_test",  y_test)

        self.dataset_name    = dataset_name
        self.preprocessing   = preprocessing
        self.preprocess_note = preprocessing_note

        self.class_names   = class_names
        self.feature_names = feature_names
        self.target_name   = target_name

        self.decimals_stats = decimals_stats
        self.language       = language
        self.software_sec   = software_section
        self.hardware_sec   = hardware_section

        # ← NUEVO: cantidad de parámetros a muestrear (user‑selectable, tope 50 en collector)
        self.params_sample_n = params_sample_n

        # ------------------- nombres -------------------------------
        self._attach_names_to_model()

        # ------------------- tiempos -------------------------------
        self.t0 = self.t1 = None
        self._ensure_times()

        # ------------------- recolección ---------------------------
        self.refresh()

    # ------------------- tiempos -------------------
    def _ensure_times(self):
        """
        Garantiza self.t0/self.t1.
        1) Usa _mlektic_t0/_mlektic_t1 (hooks).
        2) Busca nombres comunes en el modelo.
        3) Si no encuentra nada y start==end, deja al menos una diferencia mínima (1 ms)
           para evitar mostrar “0 ms”.
        """
        if self.t0 is not None and self.t1 is not None:
            return

        start = _pick_dt(self.model, "_mlektic_t0", "t0", "t_start", "start_time",
                         "train_start", "_train_start")
        end   = _pick_dt(self.model, "_mlektic_t1", "t1", "t_end", "end_time",
                         "train_end", "_train_end")

        now = _dt.now()
        if start is None and end is None:
            # No hay info: ambas a now pero forzamos delta mínimo
            start = now
            end   = now + timedelta(milliseconds=1)
        elif start is None:
            start = end
        elif end is None:
            end = now

        # Evita duración 0 ms por redondeos: fuerza +1 ms si iguales
        if start == end:
            end = end + timedelta(milliseconds=1)

        self.t0, self.t1 = start, end

    # ------------------- entrenamiento opcional -------------------
    def fit(self, **train_kw):
        """Entrena el modelo y actualiza tiempos."""
        # Además del hook, guardamos también por seguridad
        self.t0 = _dt.now()
        self.model.train((self.X_train, self.y_train), **train_kw)
        self.t1 = _dt.now()

        self._attach_names_to_model()
        self.refresh()

    # ------------------- nombres -------------------
    def _attach_names_to_model(self):
        """
        Intenta que el modelo y el builder conserven nombres reales.
        NO sobreescribe con nombres genéricos (x1, x2, ...).
        """
        has_f = hasattr(self.model, "_feature_names") and getattr(self.model, "_feature_names") is not None
        has_t = hasattr(self.model, "_target_name")   and getattr(self.model, "_target_name")   is not None

        if has_f and has_t:
            if self.feature_names is None:
                self.feature_names = list(getattr(self.model, "_feature_names"))
            if self.target_name is None:
                self.target_name = getattr(self.model, "_target_name")
            return

        fns, tn = _infer_names(self.X_train, self.y_train, self.feature_names, self.target_name)

        # Evita colgar nombres "auto" x1, x2, ... si no son necesarios
        if not has_f and fns and not _looks_auto(fns):
            try:
                setattr(self.model, "_feature_names", fns)
            except Exception:
                pass
        if not has_t and tn:
            try:
                setattr(self.model, "_target_name", tn)
            except Exception:
                pass

        if self.feature_names is None and fns:
            self.feature_names = fns
        if self.target_name is None and tn:
            self.target_name = tn

    # ------------------- recolección -------------------
    def refresh(self):
        """Vuelve a recolectar la info para el reporte."""
        self._ensure_times()
        self.data = ExperimentCollector.collect(
            model              = self.model,
            run_id             = self.run_id,
            t_start            = self.t0,
            t_end              = self.t1,
            X_train            = self.X_train,
            y_train            = self.y_train,
            X_val              = self.X_val,
            y_val              = self.y_val,
            X_test             = self.X_test,
            y_test             = self.y_test,
            dataset_name       = self.dataset_name,
            preprocessing      = self.preprocessing,
            preprocessing_note = self.preprocess_note,
            class_names        = self.class_names,
            feature_names      = self.feature_names,
            target_name        = self.target_name,
            decimals_stats     = self.decimals_stats,
            language           = self.language,
            software_section   = self.software_sec,
            hardware_section   = self.hardware_sec,
            params_sample_n    = self.params_sample_n,   # ← pasa el valor al collector
        )

    # ------------------- render -------------------
    def to_html(self, path: str | None = None, *, open_in_browser: bool = False):
        html = HTMLRenderer.render(self.data)
        if path:
            Path(path).write_text(html, encoding="utf-8")
        if open_in_browser:
            import webbrowser, tempfile, os
            tmp = path or tempfile.mktemp(suffix=".html")
            if not path:
                Path(tmp).write_text(html, encoding="utf-8")
            webbrowser.open("file://" + os.path.abspath(tmp))
        return html