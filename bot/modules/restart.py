import contextlib
from os import execl as osexecl
from sys import executable

from aiofiles import open as aiopen
from aiofiles.os import path as aiopath
from aiofiles.os import remove

from bot import LOGGER, intervals, scheduler
from bot.core.config_manager import Config
from bot.core.telegram_manager import TgClient
from bot.helper.ext_utils.bot_utils import new_task
from bot.helper.ext_utils.db_handler import database
from bot.helper.ext_utils.files_utils import clean_all
from bot.helper.telegram_helper import button_build
from bot.helper.telegram_helper.message_utils import delete_message, send_message


@new_task
async def restart_bot(_, message):
    buttons = button_build.ButtonMaker()
    buttons.data_button("Yes!", "botrestart confirm")
    buttons.data_button("Cancel", "botrestart cancel")
    button = buttons.build_menu(2)
    await send_message(
        message,
        "Are you sure you want to restart the bot ?!",
        button,
    )


async def send_incomplete_task_message(cid, msg_id, msg):
    try:
        if msg.startswith("Restarted Successfully!"):
            await TgClient.bot.edit_message_text(
                chat_id=cid,
                message_id=msg_id,
                text=msg,
            )
            await remove(".restartmsg")
        else:
            await TgClient.bot.send_message(
                chat_id=cid,
                text=msg,
                disable_notification=True,
            )
    except Exception as e:
        LOGGER.error(e)


async def restart_notification():
    if await aiopath.isfile(".restartmsg"):
        async with aiopen(".restartmsg") as f:
            content = await f.read()
            chat_id, msg_id = map(int, content.splitlines())
    else:
        chat_id, msg_id = 0, 0

    if (
        Config.INCOMPLETE_TASK_NOTIFIER
        and Config.DATABASE_URL
        and (notifier_dict := await database.get_incomplete_tasks())
    ):
        for cid, data in notifier_dict.items():
            msg = "Restarted Successfully!" if cid == chat_id else "Bot Restarted!"
            for tag, links in data.items():
                msg += f"\n\n{tag}: "
                for index, link in enumerate(links, start=1):
                    msg += f" <a href='{link}'>{index}</a> |"
                    if len(msg.encode()) > 4000:
                        await send_incomplete_task_message(cid, msg_id, msg)
                        msg = ""
            if msg:
                await send_incomplete_task_message(cid, msg_id, msg)

    if await aiopath.isfile(".restartmsg"):
        with contextlib.suppress(Exception):
            await TgClient.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text="Restarted Successfully!",
            )
        await remove(".restartmsg")


@new_task
async def confirm_restart(_, query):
    await query.answer()
    data = query.data.split()
    message = query.message
    await delete_message(message)
    if data[1] == "confirm":
        reply_to = message.reply_to_message
        intervals["stopAll"] = True
        restart_message = await send_message(reply_to, "Restarting...")
        await delete_message(message)
        await TgClient.stop()
        if scheduler.running:
            scheduler.shutdown(wait=False)
        if st := intervals["status"]:
            for intvl in list(st.values()):
                intvl.cancel()
        await clean_all()

        async with aiopen(".restartmsg", "w") as f:
            await f.write(f"{restart_message.chat.id}\n{restart_message.id}\n")
        osexecl(executable, executable, "-m", "bot")
    else:
        await delete_message(message)
