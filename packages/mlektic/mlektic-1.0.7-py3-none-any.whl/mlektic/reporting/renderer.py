# mlektic/reporting/renderer.py
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound

_THIS_DIR = Path(__file__).parent
env = Environment(
    loader=FileSystemLoader(_THIS_DIR / "templates"),
    autoescape=select_autoescape()
)

def _get_template_for_language(lang: str):
    lang = (lang or "es").lower()
    file_by_lang = {
        "es": "report_template_es.html",
        "en": "report_template_en.html",
    }
    # Compatibilidad: si falta la plantilla ES, usar la legacy
    candidates = [file_by_lang.get(lang, "report_template_es.html")]
    if lang == "es":
        candidates.append("report_template.html")  # legacy
    for name in candidates:
        try:
            return env.get_template(name)
        except TemplateNotFound:
            continue
    # Último recurso: levanta error claro
    raise TemplateNotFound(", ".join(candidates))

class HTMLRenderer:
    @staticmethod
    def render(context: dict) -> str:
        lang = (context.get("language") or "es").lower()
        template = _get_template_for_language(lang)
        return template.render(**context)
