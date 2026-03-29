from asyncio import (
    create_subprocess_exec,
    create_subprocess_shell,
    sleep,
)
from functools import partial
from io import BytesIO
from os import getcwd
from time import time

from aiofiles.os import path as aiopath
from aiofiles.os import remove
from pyrogram.filters import create
from pyrogram.handlers import MessageHandler

from bot import (
    auth_chats,
    excluded_extensions,
    included_extensions,
    intervals,
    sudo_users,
    task_dict,
)
from bot.core.config_manager import Config
from bot.core.startup import update_variables
from bot.core.telegram_manager import TgClient
from bot.helper.ext_utils.bot_utils import SetInterval, new_task
from bot.helper.ext_utils.db_handler import database
from bot.helper.ext_utils.task_manager import start_from_queued
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.telegram_helper.message_utils import (
    delete_message,
    edit_message,
    send_file,
    send_message,
    update_status_message,
)

start = 0
state = "view"
handler_dict = {}
DEFAULT_VALUES = {
    "LEECH_SPLIT_SIZE": TgClient.MAX_SPLIT_SIZE,
    "UPSTREAM_BRANCH": "main",
    "QUEUE_ALL": 12,
}


async def get_buttons(key=None, edit_type=None):
    buttons = ButtonMaker()
    if key is None:
        buttons.data_button("Config", "botset var")
        buttons.data_button("Pvt Files", "botset private")
        buttons.data_button("Close", "botset close")
        msg = "Bot Settings:"
    elif edit_type is not None:
        if edit_type == "botvar":
            msg = ""
            buttons.data_button("Back", "botset var")
            if key not in ["TELEGRAM_HASH", "TELEGRAM_API", "OWNER_ID", "BOT_TOKEN"]:
                buttons.data_button("Default", f"botset resetvar {key}")
            buttons.data_button("Close", "botset close")
            if key in [
                "CMD_SUFFIX",
                "OWNER_ID",
                "USER_SESSION_STRING",
                "TELEGRAM_HASH",
                "TELEGRAM_API",
                "BOT_TOKEN",
                "TG_PROXY",
            ]:
                msg += "Restart required for this edit to take effect! You will not see the changes in bot vars, the edit will be in database only!\n\n"
            msg += f"Send a valid value for {key}. Current value is '{Config.get(key)}'. Timeout: 60 sec"
    elif key == "var":
        conf_dict = Config.get_all()
        for k in list(conf_dict.keys())[start : 10 + start]:
            if k == "DATABASE_URL" and state != "view":
                continue
            buttons.data_button(k, f"botset botvar {k}")
        if state == "view":
            buttons.data_button("Edit", "botset edit var")
        else:
            buttons.data_button("View", "botset view var")
        buttons.data_button("Back", "botset back")
        buttons.data_button("Close", "botset close")
        for x in range(0, len(conf_dict), 10):
            buttons.data_button(
                f"{int(x / 10)}",
                f"botset start var {x}",
                position="footer",
            )
        msg = f"Config Variables | Page: {int(start / 10)} | State: {state}"
    elif key == "private":
        buttons.data_button("Back", "botset back")
        buttons.data_button("Close", "botset close")
        msg = """Send private file: config.py, token.pickle, accounts.zip, cookies.txt or any other private file!
To delete private file send only the file name as text message.
Timeout: 60 sec"""

    button = buttons.build_menu(1) if key is None else buttons.build_menu(2)
    return msg, button


async def update_buttons(message, key=None, edit_type=None):
    msg, button = await get_buttons(key, edit_type)
    await edit_message(message, msg, button)


@new_task
async def edit_variable(_, message, pre_message, key):
    handler_dict[message.chat.id] = False
    value = message.text
    if value.lower() == "true":
        value = True
    elif value.lower() == "false":
        value = False
        if key == "INCOMPLETE_TASK_NOTIFIER" and Config.DATABASE_URL:
            await database.trunc_table("tasks")
    elif key == "LEECH_SPLIT_SIZE":
        value = min(int(value), TgClient.MAX_SPLIT_SIZE)
    elif key == "EXCLUDED_EXTENSIONS":
        fx = value.split()
        excluded_extensions.clear()
        for x in fx:
            x = x.lstrip(".")
            excluded_extensions.append(x.strip().lower())
    elif key == "INCLUDED_EXTENSIONS":
        fx = value.split()
        included_extensions.clear()
        for x in fx:
            x = x.lstrip(".")
            included_extensions.append(x.strip().lower())
    elif key == "AUTHORIZED_CHATS":
        aid = value.split()
        auth_chats.clear()
        for id_ in aid:
            chat_id, *thread_ids = id_.split("|")
            chat_id = int(chat_id.strip())
            if thread_ids:
                thread_ids = [int(x.strip()) for x in thread_ids]
                auth_chats[chat_id] = thread_ids
            else:
                auth_chats[chat_id] = []
    elif key == "SUDO_USERS":
        sudo_users.clear()
        aid = value.split()
        for id_ in aid:
            sudo_users.append(int(id_.strip()))
    elif value.isdigit():
        value = int(value)
    elif (value.startswith("[") and value.endswith("]")) or (
        value.startswith("{") and value.endswith("}")
    ):
        value = eval(value)
    Config.set(key, value)
    await update_buttons(pre_message, "var")
    await delete_message(message)
    await database.update_config({key: value})
    if key in ["QUEUE_ALL", "QUEUE_DOWNLOAD", "QUEUE_UPLOAD"]:
        await start_from_queued()


@new_task
async def update_private_file(_, message, pre_message):
    handler_dict[message.chat.id] = False
    if not message.media and (file_name := message.text):
        if await aiopath.isfile(file_name) and file_name != "config.py":
            await remove(file_name)
        await delete_message(message)
    elif doc := message.document:
        file_name = doc.file_name
        fpath = f"{getcwd()}/{file_name}"
        if await aiopath.exists(fpath):
            await remove(fpath)
        await message.download(file_name=fpath)
        if file_name == "config.py":
            await load_config()
        await delete_message(message)
    await update_buttons(pre_message)
    await database.update_private_file(file_name)


async def event_handler(client, query, pfunc, rfunc, document=False):
    chat_id = query.message.chat.id
    handler_dict[chat_id] = True
    start_time = time()

    async def event_filter(_, __, event):
        user = event.from_user or event.sender_chat
        return bool(
            user.id == query.from_user.id
            and event.chat.id == chat_id
            and (event.text or (event.document and document)),
        )

    handler = client.add_handler(
        MessageHandler(pfunc, filters=create(event_filter)),
        group=-1,
    )
    while handler_dict[chat_id]:
        await sleep(0.5)
        if time() - start_time > 60:
            handler_dict[chat_id] = False
            await rfunc()
    client.remove_handler(*handler)


@new_task
async def edit_bot_settings(client, query):
    data = query.data.split()
    message = query.message
    handler_dict[message.chat.id] = False
    if data[1] == "close":
        await query.answer()
        await delete_message(message.reply_to_message)
        await delete_message(message)
    elif data[1] == "back":
        await query.answer()
        globals()["start"] = 0
        await update_buttons(message, None)
    elif data[1] == "var":
        await query.answer()
        await update_buttons(message, data[1])
    elif data[1] == "resetvar":
        await query.answer()
        expected_type = type(getattr(Config, data[2]))
        if expected_type is bool:
            value = False
        elif expected_type is int:
            value = 0
        elif expected_type is str:
            value = ""
        elif expected_type is list:
            value = []
        elif expected_type is dict:
            value = {}
        if data[2] in DEFAULT_VALUES:
            value = DEFAULT_VALUES[data[2]]
        elif data[2] == "EXCLUDED_EXTENSIONS":
            excluded_extensions.clear()
        elif data[2] == "INCLUDED_EXTENSIONS":
            included_extensions.clear()
        elif data[2] == "BASE_URL":
            await (
                await create_subprocess_exec("pkill", "-9", "-f", "gunicorn")
            ).wait()
        elif data[2] == "BASE_URL_PORT":
            value = 80
            if Config.BASE_URL:
                await (
                    await create_subprocess_exec("pkill", "-9", "-f", "gunicorn")
                ).wait()
                await create_subprocess_shell(
                    f"gunicorn -k uvicorn.workers.UvicornWorker -w 1 web.wserver:app --bind 0.0.0.0:{value}",
                )
        elif data[2] == "INCOMPLETE_TASK_NOTIFIER":
            await database.trunc_table("tasks")
        elif data[2] == "AUTHORIZED_CHATS":
            auth_chats.clear()
        elif data[2] == "SUDO_USERS":
            sudo_users.clear()
        Config.set(data[2], value)
        await update_buttons(message, "var")
        if data[2] == "DATABASE_URL":
            await database.disconnect()
        await database.update_config({data[2]: value})
        if data[2] in ["QUEUE_ALL", "QUEUE_DOWNLOAD", "QUEUE_UPLOAD"]:
            await start_from_queued()
    elif data[1] == "private":
        await query.answer()
        await update_buttons(message, data[1])
        pfunc = partial(update_private_file, pre_message=message)
        rfunc = partial(update_buttons, message)
        await event_handler(client, query, pfunc, rfunc, True)
    elif data[1] == "botvar" and state == "edit":
        await query.answer()
        await update_buttons(message, data[2], data[1])
        pfunc = partial(edit_variable, pre_message=message, key=data[2])
        rfunc = partial(update_buttons, message, "var")
        await event_handler(client, query, pfunc, rfunc)
    elif data[1] == "botvar" and state == "view":
        value = f"{Config.get(data[2])}"
        if len(value) > 200:
            await query.answer()
            with BytesIO(str.encode(value)) as out_file:
                out_file.name = f"{data[2]}.txt"
                await send_file(message, out_file)
            return
        if value == "":
            value = None
        await query.answer(f"{value}", show_alert=True)
    elif data[1] == "edit":
        await query.answer()
        globals()["state"] = "edit"
        await update_buttons(message, data[2])
    elif data[1] == "view":
        await query.answer()
        globals()["state"] = "view"
        await update_buttons(message, data[2])
    elif data[1] == "start":
        await query.answer()
        if start != int(data[3]):
            globals()["start"] = int(data[3])
            await update_buttons(message, data[2])


@new_task
async def send_bot_settings(_, message):
    handler_dict[message.chat.id] = False
    msg, button = await get_buttons()
    globals()["start"] = 0
    await send_message(message, msg, button)


async def load_config():
    Config.load()
    await update_variables()

    if len(task_dict) != 0 and (st := intervals["status"]):
        for key, intvl in list(st.items()):
            intvl.cancel()
            intervals["status"][key] = SetInterval(
                1,
                update_status_message,
                key,
            )

    if not Config.INCOMPLETE_TASK_NOTIFIER:
        await database.trunc_table("tasks")

    await (await create_subprocess_exec("pkill", "-9", "-f", "gunicorn")).wait()
    if Config.BASE_URL:
        await create_subprocess_shell(
            f"gunicorn -k uvicorn.workers.UvicornWorker -w 1 web.wserver:app --bind 0.0.0.0:{Config.BASE_URL_PORT}",
        )

    if Config.DATABASE_URL:
        await database.connect()
        config_dict = Config.get_all()
        await database.update_config(config_dict)
    else:
        await database.disconnect()
    await start_from_queued()
