from dotenv import load_dotenv
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

import ua_appointment_checker.constants as cons
from ua_appointment_checker import checker
from typing import Tuple, Callable
from loguru import logger
from ua_appointment_checker.registry import manager
from ua_appointment_checker.environment import app_environment


@manager.register("help", description="Shows help instructions.")
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
    host = app_environment.remote_chrome_hostname
    port = app_environment.remote_chrome_port
    remote_chrome_url = cons.REMOTE_CHROME_URL_FORMAT.format(
        host=host,
        port=port
    )
    with checker.get_default_remote_webdriver(remote_chrome_url) as driver:
        available = checker.are_appointments_available(
            web_driver=driver,
            target_url=cons.DEFAULT_EMBASSY_URL
        )
        if available:
            appointments = checker.get_appointments_available(
                driver=driver,
                target_url=cons.DEFAULT_EMBASSY_URL
            )
    if available:
        appointments_msg = "\n".join(
            f"* {appointment.date}: {appointment.number_of_appointments} appointments."
            for appointment in appointments
        )
        message = (
            "Appointments available.\n"
            f"{appointments_msg}\n"
            f"Please visit {cons.DEFAULT_EMBASSY_URL} to make an appointment"
        )
    else:
        message = "No appointments available"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message)

chat_ids = set()


@manager.register(
    "subscribe",
    description="Subscribe for automatic updates. The bot will only notify you when appointments are available."
)
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    message = "You've been successfully registered."
    # TODO: Currently, this is done in-memory, we should use a
    # persisten db instead.
    chat_ids.add(chat_id)
    logger.info(
        f"Successfully subscribed chat_id {chat_id}. There are now {len(chat_ids)} chats registered.")
    await update.effective_message.reply_text(message)


@manager.register(
    "unsubscribe",
    description="Unsubscribes for automatic updates."
)
async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    message = "You've been successfully unsubscribed."
    # TODO: Deal with db instead of with the in-memory set
    # of chat_ids to notify.
    chat_ids.remove(chat_id)
    logger.info(
        f"Successfully unsubscribed chat_id {chat_id}. There are now {len(chat_ids)} chats registered.")
    await update.effective_message.reply_text(message)


async def check_and_notify(context: ContextTypes.DEFAULT_TYPE):
    # TODO: Generating the host/port and url is repeated,
    # unify into one single entry point/function
    if len(chat_ids) == 0:
        logger.info("No chats to notify, we will not run polling.")
        return
    host = app_environment.remote_chrome_hostname
    port = app_environment.remote_chrome_port
    remote_chrome_url = cons.REMOTE_CHROME_URL_FORMAT.format(
        host=host,
        port=port
    )
    with checker.get_default_remote_webdriver(remote_chrome_url) as driver:
        available = checker.are_appointments_available(
            web_driver=driver,
            target_url=cons.DEFAULT_EMBASSY_URL
        )
        if available:
            appointments = checker.get_appointments_available(
                driver=driver,
                target_url=cons.DEFAULT_EMBASSY_URL
            )
    if available:
        appointments_msg = "\n".join(
            f"* {appointment.date}: {appointment.number_of_appointments} appointments."
            for appointment in appointments
        )
        message = (
            "Appointments available.\n"
            f"{appointments_msg}\n"
            f"Please visit {cons.DEFAULT_EMBASSY_URL} to make an appointment"
        )
        logger.info(
            f"Appointments available. Notifying to {len(chat_ids)} users.")
        for chat_id in chat_ids:
            await context.bot.send_message(chat_id, text=message)
    else:
        logger.info("No appointments available found. No notifications sent.")


def main():
    load_dotenv()
    token = app_environment.bot_token
    if not token:
        raise ValueError(
            "No bot token found. Please set the right env variable")
    application = ApplicationBuilder().token(token).build()
    for _, entry in manager.registry.items():
        handler = CommandHandler(entry.endpoint, entry.func)
        application.add_handler(handler)
    polling_interval_seconds = 15*60  # every 15 minutes
    application.job_queue.run_repeating(
        check_and_notify,
        interval=polling_interval_seconds
    )
    logger.info("Successfully started bot.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
