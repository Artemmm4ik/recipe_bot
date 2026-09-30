"""
Парсер рецептов — параллельный поиск на нескольких сайтах.
Поддерживает: povarenok.ru, russianfood.com, edimdoma.ru, allrecipes.com, supercook.com
"""
import asyncio
import logging
import re
from typing import List, Dict, Optional
from urllib.parse import quote_plus

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

TIMEOUT = aiohttp.ClientTimeout(total=20, connect=10)


async def fetch(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    """Скачать страницу. SSL по умолчанию включён."""
    try:
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status == 200:
                return await resp.text(errors="replace")
            logger.info(f"HTTP {resp.status} для {url}")
    except asyncio.TimeoutError:
        logger.warning(f"Таймаут: {url}")
    except Exception as e:
        logger.warning(f"Ошибка при загрузке {url}: {type(e).__name__}: {e}")
    return None


def extract_links(html: str, base: str, pattern: str, min_title: int = 5) -> List[Dict]:
    """
    Универсальный экстрактор: ищет ссылки содержащие паттерн,
    собирает title из текста или атрибута.
    """
    soup = BeautifulSoup(html, "lxml")
    results = []
    seen = set()

    for a in soup.find_all("a", href=re.compile(pattern)):
        href = a.get("href", "")
        if not href.startswith("http"):
            href = base.rstrip("/") + "/" + href.lstrip("/")

        if href in seen:
            continue
        seen.add(href)

        # Ищем заголовок: сначала вложенные теги h1-h3/span с классом *title*/*name*
        title = ""
        for tag in a.find_all(["h1", "h2", "h3", "h4", "span", "div", "p"]):
            t = tag.get_text(strip=True)
            if len(t) > min_title:
                title = t
                break
        if not title:
            title = a.get_text(strip=True).strip()
        if not title:
            title = a.get("title", "").strip()

        # Фильтруем мусор
        title = re.sub(r"\s+", " ", title).strip()
        if len(title) < min_title or len(title) > 200:
            continue
        # Исключаем навигацию, меню
        skip_words = ["войти", "login", "меню", "категор", "назад", "вперёд", "next", "prev"]
        if any(w in title.lower() for w in skip_words):
            continue

        results.append({"title": title, "url": href})
    return results


# ────────────────────────────────────────────────
#  povarenok.ru
# ────────────────────────────────────────────────
async def search_povarenok(session: aiohttp.ClientSession, query: str) -> List[Dict]:
    url = f"https://www.povarenok.ru/recipes/search/?q={quote_plus(query)}"
    html = await fetch(session, url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    results = []
    seen = set()

    # Основной паттерн — карточки рецептов
    for sel in [
        "article.item-bl",
        ".recipe-item",
        "div.item",
    ]:
        cards = soup.select(sel)
        if cards:
            for card in cards[:8]:
                a = card.select_one("a[href*='/recipes/show/']") or card.select_one("a")
                h = card.select_one("h2, h3, .name, .title")
                if a and h:
                    href = a.get("href", "")
                    title = h.get_text(strip=True)
                    if href and title and href not in seen and len(title) > 4:
                        if not href.startswith("http"):
                            href = "https://www.povarenok.ru" + href
                        seen.add(href)
                        results.append({"title": title, "url": href, "source": "povarenok.ru"})
            if results:
                break

    # Запасной вариант — все ссылки на рецепты
    if not results:
        for item in extract_links(html, "https://www.povarenok.ru", r"/recipes/show/", min_title=5):
            item["source"] = "povarenok.ru"
            results.append(item)

    return results[:5]


# ────────────────────────────────────────────────
#  russianfood.com
# ────────────────────────────────────────────────
async def search_russianfood(session: aiohttp.ClientSession, query: str) -> List[Dict]:
    url = f"https://www.russianfood.com/search/?ftext={quote_plus(query)}"
    html = await fetch(session, url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    results = []
    seen = set()

    # Пробуем несколько вариантов структуры
    for sel in [".recipes_item", ".recipe_item", ".search_result", "div.item", "li.item"]:
        cards = soup.select(sel)
        if cards:
            for card in cards[:8]:
                a = card.select_one("a")
                h = card.select_one(".recipes_item_name, .name, b, strong, h2, h3")
                if a:
                    href = a.get("href", "")
                    title = (h.get_text(strip=True) if h else a.get_text(strip=True)).strip()
                    if href and title and href not in seen and len(title) > 4:
                        if not href.startswith("http"):
                            href = "https://www.russianfood.com" + href
                        seen.add(href)
                        results.append({"title": title, "url": href, "source": "russianfood.com"})
            if results:
                break

    if not results:
        for item in extract_links(html, "https://www.russianfood.com", r"/recipes/recipe/r\d+", min_title=4):
            item["source"] = "russianfood.com"
            results.append(item)

    return results[:5]


# ────────────────────────────────────────────────
#  edimdoma.ru
# ────────────────────────────────────────────────
async def search_edimdoma(session: aiohttp.ClientSession, query: str) -> List[Dict]:
    url = f"https://www.edimdoma.ru/retsepty?search={quote_plus(query)}"
    html = await fetch(session, url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    results = []
    seen = set()

    for sel in [
        ".recipe-card",
        ".ed-recipe-card",
        "[data-testid='recipe-card']",
        "article",
        ".recipes-list__item",
    ]:
        cards = soup.select(sel)
        if cards:
            for card in cards[:8]:
                a = card.select_one("a[href*='/retsepty/']") or card.select_one("a")
                h = card.select_one("h2, h3, .ed-recipe-card__title, .recipe-title, .title")
                if a:
                    href = a.get("href", "")
                    title = (h.get_text(strip=True) if h else a.get_text(strip=True)).strip()
                    if href and title and href not in seen and len(title) > 4:
                        if not href.startswith("http"):
                            href = "https://www.edimdoma.ru" + href
                        seen.add(href)
                        results.append({"title": title, "url": href, "source": "edimdoma.ru"})
            if results:
                break

    if not results:
        for item in extract_links(html, "https://www.edimdoma.ru", r"/retsepty/\d+", min_title=4):
            item["source"] = "edimdoma.ru"
            results.append(item)

    return results[:5]


# ────────────────────────────────────────────────
#  allrecipes.com (EN)
# ────────────────────────────────────────────────
async def search_allrecipes(session: aiohttp.ClientSession, query: str) -> List[Dict]:
    url = f"https://www.allrecipes.com/search?q={quote_plus(query)}"
    html = await fetch(session, url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    results = []
    seen = set()

    # Пробуем карточки рецептов
    for sel in [
        "a.card__titleLink",
        "a[href*='/recipe/']",
        "[data-testid='recipe-card'] a",
        ".card a",
    ]:
        links = soup.select(sel)
        if links:
            for a in links[:10]:
                href = a.get("href", "")
                if "/recipe/" not in href:
                    continue
                title_tag = (
                    a.select_one("span.card__title, [class*='title'], [class*='heading']")
                    or a
                )
                title = title_tag.get_text(strip=True)
                title = re.sub(r"\s+", " ", title).strip()
                if href and title and href not in seen and len(title) > 4:
                    if not href.startswith("http"):
                        href = "https://www.allrecipes.com" + href
                    seen.add(href)
                    results.append({"title": title, "url": href, "source": "allrecipes.com"})
                if len(results) >= 5:
                    break
            if results:
                break

    return results[:5]


# ────────────────────────────────────────────────
#  food.ru (дополнительный русский источник)
# ────────────────────────────────────────────────
async def search_food_ru(session: aiohttp.ClientSession, query: str) -> List[Dict]:
    url = f"https://food.ru/search?query={quote_plus(query)}&type=recipe"
    html = await fetch(session, url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    results = []
    seen = set()

    for sel in [".recipe-card", ".search-item", "article", ".card"]:
        cards = soup.select(sel)
        if cards:
            for card in cards[:6]:
                a = card.select_one("a")
                h = card.select_one("h2, h3, .title, .name")
                if a:
                    href = a.get("href", "")
                    title = (h.get_text(strip=True) if h else a.get_text(strip=True)).strip()
                    if href and title and href not in seen and len(title) > 4:
                        if not href.startswith("http"):
                            href = "https://food.ru" + href
                        seen.add(href)
                        results.append({"title": title, "url": href, "source": "food.ru"})
            if results:
                break

    if not results:
        for item in extract_links(html, "https://food.ru", r"/recipes/\d+|/recipe/", min_title=4):
            item["source"] = "food.ru"
            results.append(item)

    return results[:5]


# ────────────────────────────────────────────────
#  ГЛАВНАЯ ФУНКЦИЯ
# ────────────────────────────────────────────────
async def search_recipes(
    ingredients: List[str],
    category_suffix_ru: str = "",
    category_suffix_en: str = "",
    lang: str = "ru",
    max_results: int = 8,
) -> List[Dict]:
    """
    Параллельный поиск рецептов на нескольких сайтах.
    Возвращает список {"title", "url", "source"}.
    """
    ing_ru = " ".join(ingredients[:5])
    ing_en = " ".join(ingredients[:5])

    query_ru = f"{ing_ru} {category_suffix_ru}".strip()
    query_en = f"{ing_en} {category_suffix_en}".strip()

    connector = aiohttp.TCPConnector(ssl=True, limit=10)
    async with aiohttp.ClientSession(connector=connector) as session:
        if lang == "ru":
            tasks = [
                search_povarenok(session, query_ru),
                search_russianfood(session, query_ru),
                search_edimdoma(session, query_ru),
                search_food_ru(session, query_ru),
                search_allrecipes(session, query_en),
            ]
        else:
            tasks = [
                search_allrecipes(session, query_en),
                search_povarenok(session, query_ru),
                search_food_ru(session, query_ru),
            ]

        gathered = await asyncio.gather(*tasks, return_exceptions=True)

    combined = []
    seen_urls = set()
    for r in gathered:
        if isinstance(r, Exception):
            logger.error(f"Ошибка в задаче парсера: {r}")
            continue
        if isinstance(r, list):
            for item in r:
                url = item.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    combined.append(item)

    return combined[:max_results]
