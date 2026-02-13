import json
from pathlib import Path
from fastapi import Request

LOCALES_PATH = Path(__file__).parent / "locales"

SUPPORTED_LANGUAGES = [
    "en", "hi", "mr", "ta", "te",
    "kn", "ml", "gu", "pa", "bn", "or"
]

_translations = {}

def setup_i18n():
    """
    Load all language files into memory at startup
    """
    global _translations
    for lang in SUPPORTED_LANGUAGES:
        file_path = LOCALES_PATH / f"{lang}.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                _translations[lang] = json.load(f)
        else:
            _translations[lang] = {}
    return True


def get_locale(request: Request = None) -> str:
    """
    Detect preferred language from Accept-Language header
    """
    if request:
        header = request.headers.get("accept-language", "").lower()
        for lang in SUPPORTED_LANGUAGES:
            if lang in header:
                return lang
    return "en"


def t(key: str, locale: str = "en") -> str:
    """
    Translate message key
    """
    return _translations.get(locale, {}).get(
        key,
        _translations.get("en", {}).get(key, key)
    )
