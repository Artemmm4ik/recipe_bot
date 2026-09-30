"""
Утилиты для определения языка и управления пользовательскими данными.
"""
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

DetectorFactory.seed = 0

# Хранение данных пользователей в памяти (для простоты)
# Структура: { user_id: { "lang": "ru"/"en", "category": "any"/... } }
user_data: dict = {}


def detect_language(text: str) -> str:
    """Определяем язык по тексту. Возвращает 'ru' или 'en'."""
    try:
        lang = detect(text)
        if lang == "ru":
            return "ru"
        return "en"
    except LangDetectException:
        return "ru"


def get_user_lang(user_id: int, text: str = None) -> str:
    """Получаем язык пользователя, при необходимости определяем по тексту."""
    if user_id in user_data and "lang" in user_data[user_id]:
        return user_data[user_id]["lang"]
    if text:
        lang = detect_language(text)
        set_user_lang(user_id, lang)
        return lang
    return "ru"


def set_user_lang(user_id: int, lang: str) -> None:
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]["lang"] = lang


def get_user_category(user_id: int) -> str:
    """Возвращает текущую категорию пользователя (по умолчанию 'any')."""
    if user_id in user_data and "category" in user_data[user_id]:
        return user_data[user_id]["category"]
    return "any"


def set_user_category(user_id: int, category: str) -> None:
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]["category"] = category
