"""
Перевод текста через Google Translate (бесплатно, без ключей).
Поддерживает любой язык через deep-translator.
Кэш в памяти — повторные вызовы мгновенные.
"""
import asyncio
import logging

from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

DetectorFactory.seed = 0
logger = logging.getLogger(__name__)

# Кэш: (hash(text), target_lang) → перевод
_cache: dict[tuple, str] = {}

# Языки для которых НЕ нужен перевод (уже поддержаны нативно или схожи)
_SKIP_TRANSLATE = {"ru", "uk"}   # UI уже на русском
_EN_LANGS = {"en", "en-us", "en-gb", "en-au", "en-ca"}


def _detect_lang(text: str) -> str:
    try:
        return detect(text[:300])
    except LangDetectException:
        return "en"


def _translate_sync(text: str, target: str) -> str:
    """Синхронный перевод. Режет на чанки если текст длинный. Retry при rate limit."""
    if not text or not text.strip():
        return text

    key = (hash(text), target)
    if key in _cache:
        return _cache[key]

    try:
        import time
        from deep_translator import GoogleTranslator

        if _detect_lang(text) == target:
            _cache[key] = text
            return text

        MAX = 4500

        def _do_translate(chunk: str) -> str:
            for attempt in range(3):
                try:
                    return GoogleTranslator(source="auto", target=target).translate(chunk)
                except Exception as e:
                    err = str(e).lower()
                    if "too many requests" in err or "rate" in err:
                        time.sleep(1.5 * (attempt + 1))
                    else:
                        raise
            return chunk

        if len(text) <= MAX:
            result = _do_translate(text)
        else:
            paras = [p for p in text.replace("\r\n", "\n").split("\n") if p.strip()]
            chunks, cur = [], ""
            for p in paras:
                if len(cur) + len(p) + 1 <= MAX:
                    cur += p + "\n"
                else:
                    if cur:
                        chunks.append(cur.strip())
                    cur = p + "\n"
            if cur:
                chunks.append(cur.strip())

            parts = []
            for chunk in chunks[:5]:
                t = _do_translate(chunk)
                parts.append(t or chunk)
            result = "\n".join(parts)

        if result:
            _cache[key] = result
            return result

    except Exception as e:
        logger.warning(f"Ошибка перевода (→{target}): {e}")

    return text


async def translate_to(text: str, lang_code: str) -> str:
    """
    Универсальный асинхронный перевод на любой язык.
    lang_code — ISO код: 'ru', 'de', 'fr', 'uk', 'es', 'zh-CN', ...
    """
    if not text:
        return text
    # Не переводим если уже на нужном языке
    if lang_code in _SKIP_TRANSLATE or lang_code in _EN_LANGS:
        # Для английского UI-текстов — возвращаем как есть
        # (перевод делается только для рецептов)
        pass

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _translate_sync, text, lang_code)


async def translate_to_russian(text: str) -> str:
    return await translate_to(text, "ru")


async def translate_to_english(text: str) -> str:
    return await translate_to(text, "en")


def is_russian(text: str) -> bool:
    return _detect_lang(text[:200]) == "ru"
