"""
Конфигурация бота: Меню, режимы, переводы.
"""

CATEGORIES = {
    "any":     {"ru": "🍽 Любой рецепт",       "en": "🍽 Any Recipe",        "emoji": "🍽"},
    "diet":    {"ru": "🥗 Диета / Легкое",      "en": "🥗 Diet / Light",      "emoji": "🥗"},
    "sport":   {"ru": "💪 Белковое",            "en": "💪 High Protein",      "emoji": "💪"},
    "dessert": {"ru": "🍰 Десерт",              "en": "🍰 Dessert",            "emoji": "🍰"},
    "vegan":   {"ru": "🌱 Без мяса",            "en": "🌱 Vegetarian",         "emoji": "🌱"},
    "quick":   {"ru": "⚡ На скорую руку",      "en": "⚡ Quick (20 min)",     "emoji": "⚡"},
    "soup":    {"ru": "🍲 Супы",                "en": "🍲 Soup",               "emoji": "🍲"},
    "keto":    {"ru": "🥑 Кето",                "en": "🥑 Keto / Low Carb",   "emoji": "🥑"},
}

TEXTS = {
    "ru": {
        "btn_menu_normal":    "🔍 Искать любые",
        "btn_menu_strict":    "🎯 Только из моих",
        "btn_menu_fridge":    "🥦 Холодильник",
        "btn_menu_fav":       "⭐ Избранное",
        "btn_menu_rand":      "🎲 Сюрприз",
        "btn_menu_cat":       "🗂 Категории",

        "welcome": (
            "👋 <b>Привет! Я Шеф-бот.</b>\n"
            "Помогу приготовить вкусно из того, что есть дома.\n\n"
            "Используй кнопки внизу:\n"
            "🔍 <b>Искать любые</b> — покажет лучшие рецепты.\n"
            "🎯 <b>Только из моих</b> — рецепты СТРОГО из твоих продуктов (без магазина).\n\n"
            "Просто нажми нужный поиск и напиши продукты!"
        ),
        "help": "ℹ️ Используй меню внизу для управления ботом. Напиши продукты через запятую, когда выберешь режим поиска.",
        
        "mode_set_normal":    "🔍 <b>Обычный поиск</b>\nНапиши продукты через запятую (например: <i>курица, картошка</i>), и я найду лучшие рецепты!",
        "mode_set_strict":    "🎯 <b>Только из моих</b>\nНапиши продукты. Я подберу рецепт так, чтобы тебе НЕ пришлось идти в магазин (соль и масло не считаются).",
        
        "choose_category":    "🗂 Выбери категорию:",
        "category_set":       "✅ Выбрано: <b>{cat}</b>",
        "searching":          "🍳 Ищу идеи из: <i>{ingredients}</i>...",
        "no_results":         "😕 Ничего не нашёл. Попробуй написать другие продукты.",
        "too_short":          "❗ Напиши хотя бы пару ингредиентов.",
        "error":              "⚠️ Упс, произошла ошибка сети. Попробуй ещё раз.",
        "btn_next":           "⏭ Другой рецепт",
        "translating":        "⏳ Открываю...",
        "no_more_recipes":    "Больше рецептов нет! Попробуй изменить продукты.",
        
        "lbl_from_your":      "Есть",
        "lbl_buy_more":       "Докупить",
        "lbl_cooking":        "Рецепт",
        "lbl_full_recipe":    "Читать полностью",
        
        "fridge_contents":    "🥦 <b>Мой холодильник:</b>\n{items}\n\nНажми поиск внизу, чтобы приготовить из них!",
        "fridge_empty":       "🥦 Холодильник пуст. Твои продукты сохранятся сюда автоматически после поиска.",
        "btn_clear_fridge":   "🗑 Очистить холодильник",
        "fridge_cleared":     "🗑 Очищено!",
        
        "favorites_empty":    "⭐ Нет сохраненных рецептов.",
        "favorites_header":   "⭐ <b>Твои сохраненные рецепты:</b>\nНажми на любой, чтобы открыть его:",
        "fav_added":          "❤️ Сохранено!",
        "fav_already":        "Уже сохранено",
        "fav_removed":        "Удалено",
        "btn_favorite":       "Сохранить",
        "btn_unfavorite":     "Убрать",
        
        "match_100":   "✅ Всё есть",
        "match_high":  "✅ Почти всё ({pct}%)",
        "match_mid":   "🟡 Нужно докупить",
        "match_low":   "🔴 Мало совпадений",
        "strict_warn": "⚠️ Идеальных нет. Показываю лучшие:",
        "random_title":  "🎲 <b>Случайный рецепт:</b>",
    },
    "en": {
        "btn_menu_normal":    "🔍 Normal Search",
        "btn_menu_strict":    "🎯 Only My Stuff",
        "btn_menu_fridge":    "🥦 Fridge",
        "btn_menu_fav":       "⭐ Favorites",
        "btn_menu_rand":      "🎲 Surprise",
        "btn_menu_cat":       "🗂 Categories",

        "welcome": (
            "👋 <b>Hi! I'm Chef Bot.</b>\n"
            "I'll help you cook with what you have.\n\n"
            "Use the menu below:\n"
            "🔍 <b>Normal</b> — best matching recipes.\n"
            "🎯 <b>Only My Stuff</b> — STRICTLY from your ingredients (no shopping).\n\n"
            "Just tap a search mode and type your ingredients!"
        ),
        "help": "ℹ️ Use the bottom menu to navigate. Type ingredients separated by commas when you select a search mode.",
        
        "mode_set_normal":    "🔍 <b>Normal Search</b>\nType your ingredients (e.g. <i>chicken, potato</i>) and I'll find recipes!",
        "mode_set_strict":    "🎯 <b>Only My Stuff</b>\nType ingredients. I'll find recipes where you don't need to go shopping.",
        
        "choose_category":    "🗂 Choose category:",
        "category_set":       "✅ Selected: <b>{cat}</b>",
        "searching":          "🍳 Finding ideas for: <i>{ingredients}</i>...",
        "no_results":         "😕 Nothing found. Try different ingredients.",
        "too_short":          "❗ Type at least a couple of ingredients.",
        "error":              "⚠️ Network error. Please try again.",
        "btn_next":           "⏭ Next recipe",
        "translating":        "⏳ Opening...",
        "no_more_recipes":    "No more recipes! Try different ingredients.",
        
        "lbl_from_your":      "Have",
        "lbl_buy_more":       "Need",
        "lbl_cooking":        "Recipe",
        "lbl_full_recipe":    "Read full",
        
        "fridge_contents":    "🥦 <b>My Fridge:</b>\n{items}\n\nTap search below to cook from these!",
        "fridge_empty":       "🥦 Fridge is empty. Ingredients save here automatically.",
        "btn_clear_fridge":   "🗑 Clear fridge",
        "fridge_cleared":     "🗑 Cleared!",
        
        "favorites_empty":    "⭐ No favorites yet.",
        "favorites_header":   "⭐ <b>Favorite recipes:</b>\nTap any to open:",
        "fav_added":          "❤️ Saved!",
        "fav_already":        "Already saved",
        "fav_removed":        "Removed",
        "btn_favorite":       "Save",
        "btn_unfavorite":     "Remove",
        
        "match_100":   "✅ Have everything",
        "match_high":  "✅ Almost everything ({pct}%)",
        "match_mid":   "🟡 Need to shop",
        "match_low":   "🔴 Missing a lot",
        "strict_warn": "⚠️ No perfect matches. Showing best:",
        "random_title":  "🎲 <b>Surprise recipe:</b>",
    },
}
