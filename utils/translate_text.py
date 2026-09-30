"""
Переводчик: последовательный перевод с микрозадержкой,
так как батчинг через разделители ломается на стороне Google.
"""
import asyncio
import logging
from functools import lru_cache

from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

DetectorFactory.seed = 0
logger = logging.getLogger(__name__)

_cache: dict[tuple, str] = {}
TRANSLATE_TIMEOUT = 10.0


def _detect_lang(text: str) -> str:
    try:
        return detect(text[:300])
    except LangDetectException:
        return "en"


def _translate_sync(text: str, target: str) -> str:
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

        for attempt in range(3):
            try:
                result = GoogleTranslator(source="auto", target=target).translate(text)
                if result:
                    _cache[key] = result
                    return result
            except Exception as e:
                err = str(e).lower()
                if "too many requests" in err or "rate" in err:
                    time.sleep(1.0 * (attempt + 1))
                else:
                    break

    except Exception as e:
        logger.warning(f"Ошибка перевода (→{target}): {e}")

    return text


async def translate_to(text: str, lang_code: str) -> str:
    if not text: return text
    key = (hash(text), lang_code)
    if key in _cache: return _cache[key]

    loop = asyncio.get_event_loop()
    try:
        return await asyncio.wait_for(
            loop.run_in_executor(None, _translate_sync, text, lang_code),
            timeout=TRANSLATE_TIMEOUT,
        )
    except Exception as e:
        logger.warning(f"translate_to error: {e}")
        return text


async def translate_many(texts: list[str], lang_code: str) -> list[str]:
    """
    Чтобы не ловить 'Too many requests' от параллельного спама, 
    и не ломать Google разделителями (батчинг глючит), 
    переводим строго по одному с микрозадержкой. 
    (5 коротких строк займут 1-2 секунды, это нормально)
    """
    if not texts:
        return []

    results = []
    for text in texts:
        if not text:
            results.append("")
            continue
            
        key = (hash(text), lang_code)
        if key in _cache:
            results.append(_cache[key])
            continue
            
        res = await translate_to(text, lang_code)
        results.append(res)
        await asyncio.sleep(0.1) # Защита от rate-limit
        
    return results
