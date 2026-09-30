"""
Перевод текста через Google Translate (бесплатно, без ключей).
Ключевые оптимизации:
- asyncio.gather() для параллельного перевода
- Агрессивный кэш
- Таймаут 5 сек, фоллбэк на английский
- Retry при rate limit
"""
import asyncio
import logging
from functools import lru_cache

from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

DetectorFactory.seed = 0
logger = logging.getLogger(__name__)

_cache: dict[tuple, str] = {}
TRANSLATE_TIMEOUT = 5.0   # секунд, после этого возвращаем оригинал


def _detect_lang(text: str) -> str:
    try:
        return detect(text[:300])
    except LangDetectException:
        return "en"


def _translate_sync(text: str, target: str) -> str:
    """Синхронный перевод с retry."""
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

        def _do(chunk: str) -> str:
            for attempt in range(3):
                try:
                    return GoogleTranslator(source="auto", target=target).translate(chunk)
                except Exception as e:
                    err = str(e).lower()
                    if "too many requests" in err or "rate" in err:
                        time.sleep(1.0 * (attempt + 1))
                    else:
                        raise
            return chunk

        if len(text) <= MAX:
            result = _do(text)
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
            parts = [_do(c) for c in chunks[:4]]
            result = "\n".join(p for p in parts if p)

        if result:
            _cache[key] = result
            return result

    except Exception as e:
        logger.warning(f"Ошибка перевода (→{target}): {e}")
    return text


async def translate_to(text: str, lang_code: str) -> str:
    """
    Асинхронный перевод с таймаутом.
    Если перевод занял > TRANSLATE_TIMEOUT секунд — возвращаем оригинал.
    """
    if not text:
        return text
    # Уже в кэше — мгновенно
    key = (hash(text), lang_code)
    if key in _cache:
        return _cache[key]

    loop = asyncio.get_event_loop()
    try:
        result = await asyncio.wait_for(
            loop.run_in_executor(None, _translate_sync, text, lang_code),
            timeout=TRANSLATE_TIMEOUT,
        )
        return result
    except asyncio.TimeoutError:
        logger.warning(f"Таймаут перевода (→{lang_code}), возвращаем оригинал")
        return text
    except Exception as e:
        logger.warning(f"translate_to error: {e}")
        return text


async def translate_many(texts: list[str], lang_code: str) -> list[str]:
    """
    Параллельный перевод списка строк.
    Все запросы запускаются одновременно через asyncio.gather().
    """
    if not texts:
        return []
    tasks = [translate_to(t, lang_code) for t in texts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # Фоллбэк на оригинал если ошибка
    return [
        r if isinstance(r, str) else texts[i]
        for i, r in enumerate(results)
    ]


async def translate_to_russian(text: str) -> str:
    return await translate_to(text, "ru")


async def translate_to_english(text: str) -> str:
    return await translate_to(text, "en")


def is_russian(text: str) -> bool:
    return _detect_lang(text[:200]) == "ru"
