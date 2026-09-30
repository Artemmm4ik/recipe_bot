"""
Словарь перевода русских ингредиентов → английские (для TheMealDB API).
"""

RU_TO_EN: dict[str, str] = {
    # ── Мясо и птица ──────────────────────────────
    "курица": "chicken",
    "куриное филе": "chicken breast",
    "куриная грудка": "chicken breast",
    "куриное бедро": "chicken thigh",
    "говядина": "beef",
    "свинина": "pork",
    "баранина": "lamb",
    "индейка": "turkey",
    "утка": "duck",
    "фарш": "ground beef",
    "мясо": "beef",
    "сало": "bacon",
    "бекон": "bacon",
    "колбаса": "sausage",
    "ветчина": "ham",

    # ── Рыба и морепродукты ────────────────────────
    "рыба": "fish",
    "лосось": "salmon",
    "семга": "salmon",
    "тунец": "tuna",
    "треска": "cod",
    "тилапия": "tilapia",
    "форель": "trout",
    "сельдь": "herring",
    "скумбрия": "mackerel",
    "креветки": "shrimp",
    "кальмар": "squid",
    "мидии": "mussels",
    "краб": "crab",

    # ── Яйца и молочные ───────────────────────────
    "яйца": "eggs",
    "яйцо": "eggs",
    "молоко": "milk",
    "сыр": "cheese",
    "творог": "cottage cheese",
    "сметана": "sour cream",
    "масло": "butter",
    "сливки": "cream",
    "йогурт": "yogurt",
    "кефир": "kefir",
    "ряженка": "yogurt",
    "пармезан": "parmesan",
    "моцарелла": "mozzarella",
    "брынза": "feta",
    "фета": "feta",

    # ── Овощи ─────────────────────────────────────
    "помидоры": "tomatoes",
    "помидор": "tomatoes",
    "томаты": "tomatoes",
    "томат": "tomatoes",
    "огурец": "cucumber",
    "огурцы": "cucumber",
    "картошка": "potato",
    "картофель": "potato",
    "картофелина": "potato",
    "лук": "onion",
    "лук репчатый": "onion",
    "зеленый лук": "spring onion",
    "лук-шалот": "shallot",
    "чеснок": "garlic",
    "морковь": "carrots",
    "морковка": "carrots",
    "болгарский перец": "bell pepper",
    "перец болгарский": "bell pepper",
    "перец": "pepper",
    "капуста": "cabbage",
    "белокочанная капуста": "cabbage",
    "брокколи": "broccoli",
    "цветная капуста": "cauliflower",
    "брюссельская капуста": "brussels sprouts",
    "баклажан": "eggplant",
    "баклажаны": "eggplant",
    "кабачок": "zucchini",
    "кабачки": "zucchini",
    "тыква": "pumpkin",
    "свекла": "beet",
    "редис": "radish",
    "сельдерей": "celery",
    "шпинат": "spinach",
    "салат": "lettuce",
    "рукола": "arugula",
    "горошек": "peas",
    "кукуруза": "corn",
    "грибы": "mushrooms",
    "шампиньоны": "mushrooms",
    "белые грибы": "mushrooms",
    "авокадо": "avocado",
    "спаржа": "asparagus",
    "артишок": "artichoke",

    # ── Фрукты ────────────────────────────────────
    "яблоко": "apple",
    "яблоки": "apple",
    "банан": "banana",
    "бананы": "banana",
    "лимон": "lemon",
    "апельсин": "orange",
    "мандарин": "orange",
    "грейпфрут": "grapefruit",
    "клубника": "strawberry",
    "малина": "raspberry",
    "черника": "blueberry",
    "вишня": "cherry",
    "персик": "peach",
    "груша": "pear",
    "виноград": "grapes",
    "ананас": "pineapple",
    "манго": "mango",
    "арбуз": "watermelon",

    # ── Крупы, мука, выпечка ──────────────────────
    "рис": "rice",
    "мука": "flour",
    "макароны": "pasta",
    "спагетти": "spaghetti",
    "гречка": "buckwheat",
    "овсянка": "oats",
    "перловка": "barley",
    "киноа": "quinoa",
    "хлеб": "bread",
    "батон": "bread",
    "тесто": "dough",
    "дрожжи": "yeast",
    "разрыхлитель": "baking powder",
    "сода": "baking soda",
    "крахмал": "cornstarch",

    # ── Бобовые ───────────────────────────────────
    "фасоль": "beans",
    "нут": "chickpeas",
    "чечевица": "lentils",
    "горох": "peas",
    "соя": "soy",
    "тофу": "tofu",

    # ── Масла и жиры ──────────────────────────────
    "оливковое масло": "olive oil",
    "подсолнечное масло": "sunflower oil",
    "растительное масло": "vegetable oil",
    "кокосовое масло": "coconut oil",

    # ── Специи и приправы ─────────────────────────
    "соль": "salt",
    "сахар": "sugar",
    "черный перец": "black pepper",
    "красный перец": "chili pepper",
    "паприка": "paprika",
    "куркума": "turmeric",
    "кориандр": "coriander",
    "тмин": "cumin",
    "имбирь": "ginger",
    "корица": "cinnamon",
    "ваниль": "vanilla",
    "петрушка": "parsley",
    "укроп": "dill",
    "базилик": "basil",
    "орегано": "oregano",
    "тимьян": "thyme",
    "розмарин": "rosemary",
    "мята": "mint",
    "лавровый лист": "bay leaf",

    # ── Соусы и прочее ────────────────────────────
    "томатная паста": "tomato paste",
    "томатный соус": "tomato sauce",
    "соевый соус": "soy sauce",
    "уксус": "vinegar",
    "майонез": "mayonnaise",
    "горчица": "mustard",
    "мед": "honey",
    "шоколад": "chocolate",
    "какао": "cocoa",
    "сахарная пудра": "powdered sugar",
    "варенье": "jam",
    "орехи": "nuts",
    "грецкий орех": "walnuts",
    "арахис": "peanuts",
    "миндаль": "almonds",
    "кешью": "cashews",
    "изюм": "raisins",
    "чернослив": "prunes",
    "лимонный сок": "lemon juice",
    "апельсиновый сок": "orange juice",
    "бульон": "broth",
    "куриный бульон": "chicken broth",
}


def translate_ingredient(word: str) -> str:
    """
    Переводит русский ингредиент на английский.
    Если не найден — возвращает оригинал (английский).
    """
    w = word.strip().lower()
    # Точное совпадение
    if w in RU_TO_EN:
        return RU_TO_EN[w]
    # Частичное совпадение (слово входит в ключ)
    for key, val in RU_TO_EN.items():
        if w in key or key in w:
            return val
    # Возвращаем как есть (возможно уже по-английски)
    return w


def translate_ingredients(ingredients: list[str]) -> list[str]:
    """Переводит список ингредиентов RU→EN."""
    result = []
    seen = set()
    for ing in ingredients:
        translated = translate_ingredient(ing)
        if translated not in seen:
            seen.add(translated)
            result.append(translated)
    return result
