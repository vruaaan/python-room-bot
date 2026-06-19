from __future__ import annotations
import asyncio
import os

from aiohttp import web
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters

from firebase import firebase_config
from service.firestore_svc import FirestoreSvc
from service.reservation_svc import ReservationSvc
from bot import Bot

CLEANUP_INTERVAL_SECONDS = 12 * 60 * 60  # 12 hours
WEBHOOK_PATH = "/webhook"


async def cleanup_loop(reservations: ReservationSvc) -> None:
    while True:
        try:
            reservations.delete_past()
            print("Deleted past reservations.")
        except Exception as e:
            print(f"Failed to delete past reservations: {e}")
        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)


async def run_webhook_server(application: Application, port: int) -> None:
    """Runs an aiohttp server that feeds incoming Telegram updates into the
    Application's update queue. This is the async-safe way to receive
    webhooks while already inside a running event loop — application.run_webhook()
    is a blocking helper that sets up its OWN loop and can't be awaited here."""

    async def handle_webhook(request: web.Request) -> web.Response:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.update_queue.put(update)
        return web.Response(status=200)

    async def handle_health(request: web.Request) -> web.Response:
        return web.Response(status=200, text="ok")

    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)
    app.router.add_get("/", handle_health)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Webhook server listening on port {port}")

    await asyncio.Event().wait()  # block forever


async def main() -> None:
    # 1. config
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise RuntimeError("BOT_TOKEN is missing. Add it to your .env file.")

    webhook_url = os.getenv("WEBHOOK_URL")  # e.g. https://your-service.run.app
    port = int(os.getenv("PORT", "8080"))

    # 2. firebase + data layer
    db = firebase_config.init()
    store = FirestoreSvc(db)
    reservations = ReservationSvc(store)

    # 3. telegram application
    application = Application.builder().token(bot_token).build()
    bot_router = Bot(application.bot, reservations)

    async def on_message(update: Update, context) -> None:
        await bot_router.consume(update)

    application.add_handler(MessageHandler(filters.TEXT, on_message))

    # 4. scheduled cleanup, runs alongside the server
    cleanup_task = asyncio.create_task(cleanup_loop(reservations))

    print("Bot running...")

    # Cloud Run requires the container to bind $PORT immediately, regardless
    # of whether the webhook URL is known yet. We always run the webhook
    # server when PORT is set by the platform; WEBHOOK_URL just controls
    # whether we *register* the webhook with Telegram on startup.
    is_cloud_run = os.getenv("PORT") is not None

    if webhook_url or is_cloud_run:
        if webhook_url:
            await application.bot.set_webhook(url=webhook_url.rstrip("/") + WEBHOOK_PATH)
        else:
            print("WEBHOOK_URL not set yet — server is up, but webhook isn't registered with Telegram.")
            print("Set WEBHOOK_URL and redeploy, or call setWebhook manually once you have the URL.")

        async with application:
            await application.start()
            try:
                await run_webhook_server(application, port)
            finally:
                await application.stop()
                cleanup_task.cancel()
    else:
        # Long polling mode — local development only, no PORT env var present.
        async with application:
            await application.start()
            await application.updater.start_polling()
            try:
                await asyncio.Event().wait()  # block forever
            finally:
                await application.updater.stop()
                await application.stop()
                cleanup_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
