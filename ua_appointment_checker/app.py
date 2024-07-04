from dotenv import load_dotenv
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

import ua_appointment_checker.constants as cons
from ua_appointment_checker import checker
from typing import Tuple, Callable
from loguru import logger
from ua_appointment_checker.registry import manager


@manager.register("start", description="")
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands_available = "\n".join(
        f"/{entry.endpoint}: {entry.description}"
        for _, entry in manager.registry.items() if entry.endpoint != "start"
    )
    start_message = (
        "Welcome! This bot allows you to receive updates whenever a new appointment "
        "in Ukraine's Embassy in SF opens. Below is a list of useful commands.\n"
        f"{commands_available}"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=start_message)


@manager.register(endpoint="check", description="Checks, right now, whether there are appointments available")
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    driver = checker.get_default_remote_webdriver(
        cons.DEFAULT_REMOTE_CHROME_URL)
    available = checker.are_appointments_available(
        web_driver=driver,
        target_url=cons.DEFAULT_EMBASSY_URL
    )
    if available:
        message = f"Appointments available. Please visit {cons.DEFAULT_EMBASSY_URL} to make an appointment"
    else:
        message = "No appointments available"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message)


def main():
    load_dotenv()
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise ValueError(
            "No bot token found. Please set the right env variable")
    application = ApplicationBuilder().token(token).build()
    for _, entry in manager.registry.items():
        handler = CommandHandler(entry.endpoint, entry.func)
        application.add_handler(handler)
    application.run_polling()
