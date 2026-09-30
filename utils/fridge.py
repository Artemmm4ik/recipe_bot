"""
"Мой холодильник" — хранение списка продуктов пользователя между сессиями.
Также хранит: избранные рецепты, статистику, режим поиска, оценки рецептов.
"""
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Файл для персистентного хранения (в текущей директории)
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_db.json")

# Кэш в памяти
_db: dict = {}


def _load() -> None:
    """Загружаем базу из файла при старте."""
    global _db
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                _db = json.load(f)
        except Exception as e:
            logger.warning(f"Не удалось загрузить user_db.json: {e}")
            _db = {}


def _save() -> None:
    """Сохраняем базу в файл."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(_db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения user_db.json: {e}")


def _user(user_id: int) -> dict:
    """Инициализирует и возвращает данные пользователя."""
    uid = str(user_id)
    if uid not in _db:
        _db[uid] = {
            "fridge": [],           # список продуктов
            "favorites": [],        # [{id, name, url}]
            "mode": "normal",       # "normal" | "strict"
            "stats": {
                "searches": 0,
                "recipes_seen": 0,
                "favorites_count": 0,
            },
            "liked": [],            # id рецептов которые понравились
            "disliked": [],         # id рецептов которые не понравились
            "joined": datetime.now().isoformat(),
        }
    return _db[str(user_id)]


# ── Холодильник ────────────────────────────────────────────────
def save_fridge(user_id: int, ingredients: list[str]) -> None:
    u = _user(user_id)
    u["fridge"] = [i.lower().strip() for i in ingredients if i.strip()]
    _save()


def get_fridge(user_id: int) -> list[str]:
    return _user(user_id).get("fridge", [])


def clear_fridge(user_id: int) -> None:
    _user(user_id)["fridge"] = []
    _save()


def add_to_fridge(user_id: int, ingredients: list[str]) -> list[str]:
    """Добавляет продукты к уже сохранённым (без дублей)."""
    u = _user(user_id)
    existing = set(u.get("fridge", []))
    for i in ingredients:
        i = i.lower().strip()
        if i and i not in existing:
            existing.add(i)
            u.setdefault("fridge", []).append(i)
    _save()
    return u["fridge"]


# ── Режим поиска ───────────────────────────────────────────────
def get_mode(user_id: int) -> str:
    """Возвращает режим: 'normal' или 'strict'."""
    return _user(user_id).get("mode", "normal")


def set_mode(user_id: int, mode: str) -> None:
    _user(user_id)["mode"] = mode
    _save()


def toggle_mode(user_id: int) -> str:
    """Переключает режим и возвращает новый."""
    current = get_mode(user_id)
    new_mode = "strict" if current == "normal" else "normal"
    set_mode(user_id, new_mode)
    return new_mode


# ── Избранное ──────────────────────────────────────────────────
def add_favorite(user_id: int, meal_id: str, name: str, url: str) -> bool:
    u = _user(user_id)
    favs = u.setdefault("favorites", [])
    if any(f["id"] == meal_id for f in favs):
        return False  # Уже есть
    favs.append({"id": meal_id, "name": name, "url": url, "saved": datetime.now().isoformat()})
    u["stats"]["favorites_count"] = len(favs)
    _save()
    return True


def remove_favorite(user_id: int, meal_id: str) -> bool:
    u = _user(user_id)
    favs = u.get("favorites", [])
    before = len(favs)
    u["favorites"] = [f for f in favs if f["id"] != meal_id]
    if len(u["favorites"]) < before:
        u["stats"]["favorites_count"] = len(u["favorites"])
        _save()
        return True
    return False


def get_favorites(user_id: int) -> list[dict]:
    return _user(user_id).get("favorites", [])


def is_favorite(user_id: int, meal_id: str) -> bool:
    return any(f["id"] == meal_id for f in get_favorites(user_id))


# ── Оценки ─────────────────────────────────────────────────────
def rate_recipe(user_id: int, meal_id: str, liked: bool) -> None:
    u = _user(user_id)
    if liked:
        if meal_id not in u.get("liked", []):
            u.setdefault("liked", []).append(meal_id)
        if meal_id in u.get("disliked", []):
            u["disliked"].remove(meal_id)
    else:
        if meal_id not in u.get("disliked", []):
            u.setdefault("disliked", []).append(meal_id)
        if meal_id in u.get("liked", []):
            u["liked"].remove(meal_id)
    _save()


# ── Статистика ─────────────────────────────────────────────────
def inc_stat(user_id: int, field: str, amount: int = 1) -> None:
    u = _user(user_id)
    u["stats"][field] = u["stats"].get(field, 0) + amount
    _save()


def get_stats(user_id: int) -> dict:
    return _user(user_id).get("stats", {})


# Загружаем при импорте
_load()
