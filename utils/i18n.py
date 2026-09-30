"""
Интернационализация (i18n) — динамический перевод интерфейса на любой язык.

Логика:
- "ru", "uk" → используем TEXTS["ru"] (готовый перевод)
- "en"        → используем TEXTS["en"] (готовый перевод)
- Любой другой → переводим TEXTS["en"] через Google Translate (кэш)
"""
import asyncio
import logging

from config import TEXTS
from utils.translate_text import translate_to

logger = logging.getLogger(__name__)

# Кэш переведённых интерфейсных строк: (lang_code, key) → translated_text
_ui_cache: dict[tuple, str] = {}

# Языки с готовым интерфейсом
_NATIVE = {"ru": "ru", "uk": "ru"}    # Ukrainian → use Russian interface


async def get_text(key: str, lang_code: str) -> str:
    """
    Получить строку интерфейса на нужном языке.
    Автоматически переводит для языков без готового перевода.
    """
    # Встроенные языки
    if lang_code in _NATIVE:
        return TEXTS[_NATIVE[lang_code]][key]
    if lang_code.startswith("en"):
        return TEXTS["en"][key]

    # Проверяем кэш
    cache_key = (lang_code, key)
    if cache_key in _ui_cache:
        return _ui_cache[cache_key]

    # Переводим с английского
    en_text = TEXTS["en"][key]
    try:
        translated = await translate_to(en_text, lang_code)
        _ui_cache[cache_key] = translated
        return translated
    except Exception as e:
        logger.warning(f"i18n ошибка ({lang_code}, {key}): {e}")
        return en_text


async def get_texts(lang_code: str) -> dict:
    """
    Получить все строки интерфейса для данного языка.
    Для кэшированных языков — быстро, для новых — переводит один раз.
    """
    if lang_code in _NATIVE:
        return TEXTS[_NATIVE[lang_code]]
    if lang_code.startswith("en"):
        return TEXTS["en"]

    # Переводим все ключи параллельно
    keys = list(TEXTS["en"].keys())
    tasks = [get_text(k, lang_code) for k in keys]
    values = await asyncio.gather(*tasks, return_exceptions=True)

    result = {}
    for k, v in zip(keys, values):
        result[k] = v if isinstance(v, str) else TEXTS["en"][k]
    return result


async def translate_category_name(name: str, lang_code: str) -> str:
    """Переводит название категории на нужный язык."""
    if lang_code in _NATIVE or lang_code.startswith("en"):
        return name
    cache_key = (lang_code, f"cat:{name}")
    if cache_key in _ui_cache:
        return _ui_cache[cache_key]
    translated = await translate_to(name, lang_code)
    _ui_cache[cache_key] = translated
    return translated
