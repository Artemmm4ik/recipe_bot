"""
Recipe Telegram Bot — финальная версия с Каруселью.
"""
import os
import asyncio
import logging
from aiohttp import web
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters,
)

from handlers.start   import start_handler, help_handler
from handlers.category import category_handler, category_callback
from handlers.recipe  import recipe_message_handler, random_handler, carousel_callback
from handlers.fridge  import (
    fridge_handler, whatcook_handler, mode_handler,
    favorites_handler, stats_handler, fridge_callback,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def build_app(token: str) -> Application:
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start",     start_handler))
    app.add_handler(CommandHandler("help",      help_handler))
    app.add_handler(CommandHandler("category",  category_handler))
    app.add_handler(CommandHandler("fridge",    fridge_handler))
    app.add_handler(CommandHandler("whatcook",  whatcook_handler))
    app.add_handler(CommandHandler("mode",      mode_handler))
    app.add_handler(CommandHandler("random",    random_handler))
    app.add_handler(CommandHandler("favorites", favorites_handler))
    app.add_handler(CommandHandler("stats",     stats_handler))

    # Карусель рецептов
    app.add_handler(CallbackQueryHandler(carousel_callback, pattern="^carousel_next"))
    
    # Категории и холодильник
    app.add_handler(CallbackQueryHandler(category_callback, pattern="^cat_"))
    app.add_handler(CallbackQueryHandler(fridge_callback,   pattern="^(fridge_|mode_|fav_)"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, recipe_message_handler))

    return app


async def run_webhook(token: str, webhook_url: str, port: int) -> None:
    tg_app = build_app(token)
    webhook_path = f"/webhook/{token}"
    full_url = f"{webhook_url.rstrip('/')}{webhook_path}"

    await tg_app.initialize()
    await tg_app.start()
    await tg_app.bot.set_webhook(
        url=full_url,
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )
    logger.info(f"Webhook: {full_url}")

    async def tg_webhook(request: web.Request) -> web.Response:
        try:
            update = Update.de_json(await request.json(), tg_app.bot)
            await tg_app.process_update(update)
        except Exception as e:
            logger.error(f"Update error: {e}")
        return web.Response(status=200)

    async def health(_: web.Request) -> web.Response:
        return web.Response(text="OK", status=200)

    web_app = web.Application()
    web_app.router.add_get("/",       health)
    web_app.router.add_get("/health", health)
    web_app.router.add_post(webhook_path, tg_webhook)

    runner = web.AppRunner(web_app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", port).start()
    logger.info(f"Server on port {port}")

    try:
        await asyncio.Event().wait()
    finally:
        await tg_app.stop()
        await tg_app.shutdown()
        await runner.cleanup()


def run_polling(token: str) -> None:
    logger.info("Polling mode (development)...")
    build_app(token).run_polling(drop_pending_updates=True)


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN не задан!")

    webhook_url = os.getenv("WEBHOOK_URL", "").strip()
    port        = int(os.getenv("PORT", 10000))

    if webhook_url:
        asyncio.run(run_webhook(token, webhook_url, port))
    else:
        run_polling(token)


if __name__ == "__main__":
    main()
