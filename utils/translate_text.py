"""
Переводчик с многоуровневым Fallback'ом, 
так как Google Translate банит IP на бесплатных серверах.
"""
import asyncio
import logging

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
        if _detect_lang(text) == target:
            _cache[key] = text
            return text
            
        import time
        from deep_translator import GoogleTranslator, MyMemoryTranslator

        # 1. Пробуем Google
        for attempt in range(2):
            try:
                res = GoogleTranslator(source="auto", target=target).translate(text)
                if res:
                    _cache[key] = res
                    return res
            except Exception as e:
                err = str(e).lower()
                if "too many requests" in err or "rate" in err:
                    time.sleep(0.5)
                else:
                    break

        # 2. Если Google забанил IP, пробуем MyMemory (формат ru-RU)
        target_mymemory = "ru-RU" if target == "ru" else f"{target}-{target.upper()}"
        source_mymemory = "en-GB"
        try:
            res = MyMemoryTranslator(source=source_mymemory, target=target_mymemory).translate(text)
            if res:
                _cache[key] = res
                return res
        except Exception as e:
            logger.warning(f"MyMemory fallback error: {e}")

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
    """Переводит по одному с fallback API."""
    if not texts: return []

    results = []
    for text in texts:
        if not text:
            results.append("")
            continue
        res = await translate_to(text, lang_code)
        results.append(res)
        await asyncio.sleep(0.05)
        
    return results
