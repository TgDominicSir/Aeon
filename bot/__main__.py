# ruff: noqa: E402, PLC0415
from asyncio import gather

from pyrogram.types import BotCommand

from . import LOGGER, bot_loop
from .core.config_manager import Config, SystemEnv

LOGGER.info("Loading config...")
Config.load()
SystemEnv.load()

from .core.startup import load_settings

bot_loop.run_until_complete(load_settings())

from .core.telegram_manager import TgClient
from .helper.telegram_helper.bot_commands import BotCommands

COMMANDS = {
    "YtdlCommand": "- Start download using yt-dlp",
    "YtdlLeechCommand": "- Leech link using yt-dlp",
    "MediaInfoCommand": "- Get media information",
    "ForceStartCommand": "- Force start a task from queue",
    "UserSetCommand": "- User settings",
    "StatusCommand": "- Show status",
    "StatsCommand": "- Show Bot and System stats",
    "CancelAllCommand": "- Cancel all your tasks",
    "HelpCommand": "- Get detailed help",
    "SpeedTest": "- Run a speedtest",
    "BotSetCommand": "- [ADMIN] Open Bot settings",
    "LogCommand": "- [ADMIN] View bot log",
    "RestartCommand": "- [ADMIN] Restart the bot",
}


COMMAND_OBJECTS = [
    BotCommand(
        getattr(BotCommands, cmd)[0]
        if isinstance(getattr(BotCommands, cmd), list)
        else getattr(BotCommands, cmd),
        description,
    )
    for cmd, description in COMMANDS.items()
]


async def set_commands():
    if Config.SET_COMMANDS:
        await TgClient.bot.set_bot_commands(COMMAND_OBJECTS)


async def main():
    from .core.startup import (
        load_configurations,
        save_settings,
        update_variables,
    )

    await gather(TgClient.start_bot(), TgClient.start_user())
    await gather(load_configurations(), update_variables())

    from .helper.ext_utils.files_utils import clean_all
    from .helper.ext_utils.telegraph_helper import telegraph
    from .modules import (
        get_packages_version,
        restart_notification,
    )

    await gather(
        set_commands(),
    )
    await gather(
        save_settings(),
        clean_all(),
        get_packages_version(),
        restart_notification(),
        telegraph.create_account(),
    )


bot_loop.run_until_complete(main())

from .core.handlers import add_handlers
from .helper.ext_utils.bot_utils import create_help_buttons

create_help_buttons()
add_handlers()


LOGGER.info("Bot Started!")
bot_loop.run_forever()
