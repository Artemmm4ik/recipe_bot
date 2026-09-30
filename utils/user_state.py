"""
Управление состоянием пользователей.
Хранит: lang_code (полный, например "de","uk","fr"), ui_lang ("ru"/"en"), category.
"""
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

DetectorFactory.seed = 0

# Структура: { user_id: { "lang_code": "de", "ui_lang": "en", "category": "any" } }
user_data: dict = {}


def normalize_lang_code(code: str) -> str:
    """Нормализует код языка Telegram: 'en-US' → 'en', 'zh-hans' → 'zh-CN'."""
    if not code:
        return "ru"
    code = code.lower().split("-")[0].split("_")[0]
    # Маппинг нестандартных кодов
    aliases = {
        "zh": "zh-CN",
        "pt": "pt",
        "nb": "no",   # Norwegian Bokmål → Norwegian
        "iw": "he",   # старый код Hebrew
    }
    return aliases.get(code, code)


def get_ui_lang(lang_code: str) -> str:
    """
    Возвращает язык для статических текстов интерфейса.
    Русский и украинский → 'ru', всё остальное → 'en'.
    """
    if lang_code.startswith("ru") or lang_code.startswith("uk"):
        return "ru"
    return "en"


def set_user_lang(user_id: int, lang_code: str) -> None:
    """Сохраняет полный код языка пользователя."""
    if user_id not in user_data:
        user_data[user_id] = {}
    normalized = normalize_lang_code(lang_code)
    user_data[user_id]["lang_code"] = normalized
    user_data[user_id]["ui_lang"] = get_ui_lang(normalized)


def get_user_lang_code(user_id: int) -> str:
    """Возвращает полный код языка (для перевода контента)."""
    if user_id in user_data and "lang_code" in user_data[user_id]:
        return user_data[user_id]["lang_code"]
    return "ru"


def get_user_lang(user_id: int) -> str:
    """
    Возвращает язык для интерфейсных текстов ('ru' или 'en').
    Оставлен для обратной совместимости.
    """
    if user_id in user_data and "ui_lang" in user_data[user_id]:
        return user_data[user_id]["ui_lang"]
    return "ru"


def get_user_category(user_id: int) -> str:
    if user_id in user_data and "category" in user_data[user_id]:
        return user_data[user_id]["category"]
    return "any"


def set_user_category(user_id: int, category: str) -> None:
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]["category"] = category
