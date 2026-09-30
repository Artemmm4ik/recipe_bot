"""
Юнит-тесты для recipe_bot.
Запускай: python test_all.py
Не требует сети и Telegram-токена — проверяет всю логику локально.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASS = 0
FAIL = 0


def ok(name: str):
    global PASS
    PASS += 1
    print(f"  ✅ {name}")


def fail(name: str, reason: str):
    global FAIL
    FAIL += 1
    print(f"  ❌ {name}: {reason}")


# ─── 1. Импорты ─────────────────────────────────────────────────
def test_imports():
    print("\n[1] Проверка импортов")
    try:
        import config
        ok("config.py")
    except Exception as e:
        fail("config.py", str(e))
    try:
        from utils.user_state import (
            get_user_lang, set_user_lang,
            get_user_category, set_user_category, user_data,
        )
        ok("utils/user_state.py")
    except Exception as e:
        fail("utils/user_state.py", str(e))
    try:
        from parsers.recipe_parser import search_recipes, extract_links
        ok("parsers/recipe_parser.py")
    except Exception as e:
        fail("parsers/recipe_parser.py", str(e))
    try:
        from handlers.recipe import parse_ingredients
        ok("handlers/recipe.py")
    except Exception as e:
        fail("handlers/recipe.py", str(e))


# ─── 2. Config ──────────────────────────────────────────────────
def test_config():
    print("\n[2] Проверка config.py")
    from config import CATEGORIES, TEXTS

    if len(CATEGORIES) == 8:
        ok(f"Количество категорий: {len(CATEGORIES)}")
    else:
        fail("Категории", f"ожидалось 8, получено {len(CATEGORIES)}")

    for key, data in CATEGORIES.items():
        for field in ("ru", "en", "emoji", "query_suffix_ru", "query_suffix_en"):
            if field not in data:
                fail(f"CATEGORIES[{key}]", f"нет поля '{field}'")
                break
        else:
            ok(f"CATEGORIES[{key}] — все поля есть")

    for lang in ("ru", "en"):
        for key in ("welcome", "help", "choose_category", "category_set",
                    "searching", "no_results", "results_header", "too_short",
                    "current_category", "error"):
            if key not in TEXTS[lang]:
                fail(f"TEXTS[{lang}]", f"нет ключа '{key}'")
                break
        else:
            ok(f"TEXTS[{lang}] — все ключи есть")


# ─── 3. User state ──────────────────────────────────────────────
def test_user_state():
    print("\n[3] Проверка user_state")
    from utils.user_state import (
        get_user_lang, set_user_lang,
        get_user_category, set_user_category,
    )

    uid = 999999

    set_user_lang(uid, "ru")
    assert get_user_lang(uid) == "ru", "Язык не сохранился"
    ok("set/get_user_lang RU")

    set_user_lang(uid, "en")
    assert get_user_lang(uid) == "en"
    ok("set/get_user_lang EN")

    assert get_user_category(uid) == "any", "Дефолтная категория должна быть 'any'"
    ok("Дефолтная категория = 'any'")

    set_user_category(uid, "diet")
    assert get_user_category(uid) == "diet"
    ok("set/get_user_category diet")

    set_user_category(uid, "keto")
    assert get_user_category(uid) == "keto"
    ok("set/get_user_category keto")


# ─── 4. parse_ingredients ───────────────────────────────────────
def test_parse_ingredients():
    print("\n[4] Проверка parse_ingredients")
    from handlers.recipe import parse_ingredients

    cases = [
        ("курица, картошка, лук", 3),
        ("eggs; milk\nflour", 3),
        ("яблоко", 1),
        ("", 0),
        ("  , , ", 0),
        ("томаты\nогурцы\nперец\nлук", 4),
        ("a", 0),  # слишком короткий (len < 2)
    ]
    for inp, expected in cases:
        got = parse_ingredients(inp)
        if len(got) == expected:
            ok(f'"{inp[:30]}" → {got}')
        else:
            fail(f'"{inp[:30]}"', f"ожидалось {expected}, получено {len(got)}: {got}")


# ─── 5. HTML парсинг ────────────────────────────────────────────
def test_html_parsing():
    print("\n[5] Проверка HTML-парсинга (без сети)")
    from parsers.recipe_parser import extract_links

    # Тест povarenok-style
    html_pov = """<html><body>
      <a href="/recipes/show/1"><h2>Курица в духовке</h2></a>
      <a href="/recipes/show/2"><h2>Борщ классический</h2></a>
      <a href="/recipes/show/3"><h2>Оливье</h2></a>
      <a href="/about"><span>О нас</span></a>
      <a href="/login">Войти</a>
    </body></html>"""

    links = extract_links(html_pov, "https://www.povarenok.ru", r"/recipes/show/")
    if len(links) == 3:
        ok(f"Нашёл 3 рецепта, отфильтровал навигацию")
    else:
        fail("povarenok-style", f"ожидалось 3, получено {len(links)}")

    for l in links:
        assert l["url"].startswith("https://"), f"URL должен быть абсолютным: {l['url']}"
    ok("Все URL абсолютные")

    # Тест allrecipes-style
    html_all = """<html><body>
      <a href="/recipe/12345/chicken-rice"><span class="card__title">Chicken Rice Bowl</span></a>
      <a href="/recipe/67890/pasta"><span class="card__title">Easy Pasta</span></a>
      <a href="/categories/main">Main Courses</a>
    </body></html>"""

    links2 = extract_links(html_all, "https://www.allrecipes.com", r"/recipe/\d+")
    if len(links2) == 2:
        ok(f"allrecipes-style: нашёл 2 рецепта")
    else:
        fail("allrecipes-style", f"ожидалось 2, получено {len(links2)}")

    # Пустой HTML
    links3 = extract_links("<html><body></body></html>", "https://example.com", r"/recipe/")
    assert len(links3) == 0
    ok("Пустой HTML → 0 результатов")


# ─── 6. main.py структура ───────────────────────────────────────
def test_main_structure():
    print("\n[6] Проверка main.py")
    import ast, pathlib
    src = pathlib.Path("main.py").read_text()
    tree = ast.parse(src)
    funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef | ast.FunctionDef)]

    for fn in ("health_check", "build_app", "run_webhook", "run_polling", "main"):
        if fn in funcs:
            ok(f"Функция '{fn}' присутствует")
        else:
            fail(f"main.py", f"функция '{fn}' не найдена")

    if "WEBHOOK_URL" in src:
        ok("WEBHOOK_URL используется (webhook режим)")
    if "PORT" in src:
        ok("PORT читается из env (правильно для render.com)")
    if "/health" in src:
        ok("Health-check эндпоинт /health присутствует")


# ─── 7. Асинхронный тест user_state ────────────────────────────
async def test_async_flow():
    print("\n[7] Async flow тест")
    from utils.user_state import set_user_lang, set_user_category, get_user_lang, get_user_category

    users = [(1001, "ru", "diet"), (1002, "en", "sport"), (1003, "ru", "dessert")]
    for uid, lang, cat in users:
        set_user_lang(uid, lang)
        set_user_category(uid, cat)

    for uid, lang, cat in users:
        assert get_user_lang(uid) == lang
        assert get_user_category(uid) == cat
    ok(f"Состояние {len(users)} пользователей сохранено корректно")


# ─── Итог ───────────────────────────────────────────────────────
async def main():
    print("=" * 55)
    print("  🧪 Recipe Bot — Полная проверка проекта")
    print("=" * 55)

    test_imports()
    test_config()
    test_user_state()
    test_parse_ingredients()
    test_html_parsing()
    test_main_structure()
    await test_async_flow()

    print("\n" + "=" * 55)
    total = PASS + FAIL
    print(f"  Итого: {total} тестов | ✅ {PASS} прошли | ❌ {FAIL} провалились")
    print("=" * 55)

    if FAIL > 0:
        print("\n⚠️  Есть ошибки — исправь перед деплоем!")
        sys.exit(1)
    else:
        print("\n✅ Все тесты прошли! Проект готов к деплою на render.com")


if __name__ == "__main__":
    asyncio.run(main())
