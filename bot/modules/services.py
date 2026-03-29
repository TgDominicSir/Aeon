from time import time
from bot import bot_start_time
from bot.helper.ext_utils.bot_utils import new_task
from bot.helper.telegram_helper.message_utils import send_message, edit_message, send_file

@new_task
async def start(client, message):
    await send_message(message, "Bot is running! All credits to Dominic.")

@new_task
async def ping(client, message):
    start_t = time()
    reply = await send_message(message, "Ping...")
    if isinstance(reply, str): return
    end_t = time()
    await edit_message(reply, f"Pong! {round((end_t - start_t) * 1000)}ms")

@new_task
async def log(client, message):
    await send_file(message, "log.txt")

async def dominic_callback(client, query):
    await query.answer()
