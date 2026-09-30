"""
Продукты-"базовые" — они есть у всех.
При строгом поиске их не считаем "недостающими".
"""

# На английском (для сравнения с TheMealDB)
PANTRY_STAPLES_EN: set[str] = {
    # Жиры/масла
    "oil", "olive oil", "vegetable oil", "sunflower oil", "coconut oil",
    "butter", "margarine", "cooking spray", "lard", "shortening",
    # Соль, перец, специи
    "salt", "pepper", "black pepper", "white pepper", "red pepper", "cayenne",
    "paprika", "cumin", "coriander", "turmeric", "cinnamon", "nutmeg",
    "oregano", "basil", "thyme", "rosemary", "bay leaves", "bay leaf",
    "parsley", "dill", "mint", "sage", "tarragon", "cloves", "cardamom",
    "allspice", "ginger powder", "garlic powder", "onion powder",
    "chili powder", "curry powder", "italian seasoning", "mixed herbs",
    "seasoning", "spice", "spices", "herbs",
    # Сахар и выпечка
    "sugar", "brown sugar", "powdered sugar", "icing sugar",
    "baking powder", "baking soda", "bicarbonate of soda", "yeast",
    "cornstarch", "corn starch", "flour",
    # Жидкости
    "water", "ice", "cold water", "boiling water",
    # Кислоты
    "vinegar", "white vinegar", "apple cider vinegar", "balsamic vinegar",
    "lemon juice", "lime juice",
    # Соусы-основы
    "soy sauce", "worcestershire sauce", "hot sauce", "tabasco",
    "vanilla", "vanilla extract", "almond extract",
    # Бульон
    "stock", "broth", "chicken broth", "beef broth", "vegetable broth",
    "chicken stock", "beef stock", "vegetable stock", "bouillon",
    # Прочие мелочи
    "tomato paste", "tomato puree", "mustard", "honey",
    "maple syrup", "molasses",
}

# Русские эквиваленты для отображения
PANTRY_STAPLES_RU: set[str] = {
    "масло", "оливковое масло", "растительное масло", "подсолнечное масло",
    "сливочное масло", "маргарин",
    "соль", "перец", "черный перец", "белый перец", "красный перец",
    "паприка", "куркума", "тмин", "кориандр", "корица", "мускатный орех",
    "орегано", "базилик", "тимьян", "розмарин", "лавровый лист",
    "петрушка", "укроп", "мята", "гвоздика", "кардамон", "имбирь молотый",
    "чесночный порошок", "приправа", "специи", "пряности",
    "сахар", "коричневый сахар", "сахарная пудра",
    "разрыхлитель", "сода", "дрожжи", "крахмал", "мука",
    "вода", "лед",
    "уксус", "яблочный уксус", "бальзамический уксус",
    "лимонный сок", "сок лимона",
    "соевый соус", "вустерский соус", "томатная паста",
    "ваниль", "ванильный экстракт", "мед",
    "бульон", "куриный бульон", "говяжий бульон", "овощной бульон",
    "горчица", "майонез",
}


def is_staple(ingredient_en: str) -> bool:
    """Проверяет, является ли ингредиент базовым (есть у всех)."""
    ing = ingredient_en.lower().strip()
    # Прямое совпадение
    if ing in PANTRY_STAPLES_EN:
        return True
    # Частичное совпадение (например "pinch of salt" → "salt")
    for staple in PANTRY_STAPLES_EN:
        if staple in ing:
            return True
    return False


def filter_non_staples(ingredients: list[str]) -> list[str]:
    """Убирает базовые продукты из списка — остаются только 'настоящие' ингредиенты."""
    return [i for i in ingredients if not is_staple(i)]
