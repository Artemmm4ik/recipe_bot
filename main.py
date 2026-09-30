"""
Recipe Telegram Bot — оптимизирован для render.com.

Render.com требует:
1. Слушать на PORT из переменной окружения
2. Отвечать на HTTP health-check (GET /)
3. Работать через webhook (не polling — иначе таймаут)
"""
import os
import logging
from aiohttp import web
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from handlers.start import start_handler, help_handler
from handlers.category import category_handler, category_callback
from handlers.recipe import recipe_message_handler

load_dotenv()

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def health_check(request: web.Request) -> web.Response:
    """Health-check эндпоинт — render.com проверяет что сервис жив."""
    return web.Response(text="✅ Recipe Bot is running!", status=200)


def build_app(token: str) -> Application:
    """Строим Telegram Application и регистрируем хендлеры."""
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("category", category_handler))
    app.add_handler(CallbackQueryHandler(category_callback, pattern="^cat_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, recipe_message_handler))

    return app


async def run_webhook(token: str, webhook_url: str, port: int) -> None:
    """Запуск в режиме webhook (для render.com)."""
    tg_app = build_app(token)

    # Устанавливаем webhook в Telegram
    webhook_path = f"/webhook/{token}"
    full_webhook_url = f"{webhook_url.rstrip('/')}{webhook_path}"
    logger.info(f"Устанавливаем webhook: {full_webhook_url}")

    # Инициализируем приложение
    await tg_app.initialize()
    await tg_app.bot.set_webhook(
        url=full_webhook_url,
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )
    await tg_app.start()

    # aiohttp сервер для webhook + health check
    async def telegram_webhook(request: web.Request) -> web.Response:
        try:
            data = await request.json()
            update = Update.de_json(data, tg_app.bot)
            await tg_app.process_update(update)
        except Exception as e:
            logger.error(f"Ошибка обработки update: {e}")
        return web.Response(status=200)

    web_app = web.Application()
    web_app.router.add_get("/", health_check)
    web_app.router.add_get("/health", health_check)
    web_app.router.add_post(webhook_path, telegram_webhook)

    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()

    logger.info(f"✅ Сервер запущен на порту {port}")
    logger.info(f"✅ Webhook активен: {full_webhook_url}")

    # Держим процесс живым
    import asyncio
    try:
        await asyncio.Event().wait()
    finally:
        await tg_app.stop()
        await tg_app.shutdown()
        await runner.cleanup()


async def run_polling(token: str) -> None:
    """Локальный режим polling (только для разработки)."""
    logger.info("🔧 Запуск в режиме polling (только для локальной разработки)...")
    tg_app = build_app(token)
    await tg_app.run_polling(drop_pending_updates=True)


def main() -> None:
    import asyncio

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise ValueError(
            "❌ TELEGRAM_BOT_TOKEN не задан!\n"
            "Добавь его в переменные окружения render.com или в файл .env"
        )

    webhook_url = os.getenv("WEBHOOK_URL", "").strip()
    port = int(os.getenv("PORT", 10000))

    if webhook_url:
        # Render.com: webhook режим
        asyncio.run(run_webhook(token, webhook_url, port))
    else:
        # Локально: polling режим
        asyncio.run(run_polling(token))


if __name__ == "__main__":
    main()
