from asyncio import create_subprocess_shell
from os import environ

import aiohttp
from aiofiles import open as aiopen
from aiofiles.os import makedirs
from aiofiles.os import path as aiopath
from aioshutil import rmtree

from bot import (
    LOGGER,
    auth_chats,
    excluded_extensions,
    included_extensions,
    sudo_users,
    user_data,
)
from bot.helper.ext_utils.db_handler import database

from .config_manager import Config
from .telegram_manager import TgClient


async def load_settings():
    """Loads bot settings from the database (if DATABASE_URL is set)
    and applies them to the current runtime configuration.
    """
    if not Config.DATABASE_URL:
        return
    for p in ["thumbnails", "tokens", "rclone"]:
        if await aiopath.exists(p):
            await rmtree(p, ignore_errors=True)
    await database.connect()
    if database.db is not None:
        BOT_ID = Config.BOT_TOKEN.split(":", 1)[0]
        current_deploy_config = Config.get_all()
        old_deploy_config = await database.db.settings.deployConfig.find_one(
            {"_id": BOT_ID},
            {"_id": 0},
        )

        if old_deploy_config is None:
            await database.db.settings.deployConfig.replace_one(
                {"_id": BOT_ID},
                current_deploy_config,
                upsert=True,
            )
        elif old_deploy_config != current_deploy_config:
            runtime_config = (
                await database.db.settings.config.find_one(
                    {"_id": BOT_ID},
                    {"_id": 0},
                )
                or {}
            )

            new_vars = {
                k: v
                for k, v in current_deploy_config.items()
                if k not in runtime_config
            }
            if new_vars:
                runtime_config.update(new_vars)
                await database.db.settings.config.replace_one(
                    {"_id": BOT_ID},
                    runtime_config,
                    upsert=True,
                )
                LOGGER.info(f"Added new variables: {list(new_vars.keys())}")

            await database.db.settings.deployConfig.replace_one(
                {"_id": BOT_ID},
                current_deploy_config,
                upsert=True,
            )

        runtime_config = await database.db.settings.config.find_one(
            {"_id": BOT_ID},
            {"_id": 0},
        )
        if runtime_config:
            Config.load_dict(runtime_config)

        if pf_dict := await database.db.settings.files.find_one(
            {"_id": BOT_ID},
            {"_id": 0},
        ):
            for key, value in pf_dict.items():
                if value:
                    file_ = key.replace("__", ".")
                    async with aiopen(file_, "wb+") as f:
                        await f.write(value)

        if await database.db.users.find_one():
            for p in ["thumbnails", "tokens"]:
                if not await aiopath.exists(p):
                    await makedirs(p)
            rows = database.db.users.find({})
            async for row in rows:
                uid = row["_id"]
                del row["_id"]
                thumb_path = f"thumbnails/{uid}.jpg"
                if row.get("THUMBNAIL"):
                    async with aiopen(thumb_path, "wb+") as f:
                        await f.write(row["THUMBNAIL"])
                    row["THUMBNAIL"] = thumb_path
                user_data[uid] = row
            LOGGER.info("User data has been imported from the Database.")


async def save_settings():
    """Saves the current bot configuration to the database if DATABASE_URL is set."""
    if database.db is None:
        return
    config_dict = Config.get_all()
    await database.db.settings.config.replace_one(
        {"_id": TgClient.ID},
        config_dict,
        upsert=True,
    )


async def update_variables():
    """Updates various global configuration variables and lists based on the
    loaded Config values.
    """
    if (
        Config.LEECH_SPLIT_SIZE > TgClient.MAX_SPLIT_SIZE
        or Config.LEECH_SPLIT_SIZE == 2097152000
        or not Config.LEECH_SPLIT_SIZE
    ):
        Config.LEECH_SPLIT_SIZE = TgClient.MAX_SPLIT_SIZE

    Config.HYBRID_LEECH = bool(Config.HYBRID_LEECH and TgClient.IS_PREMIUM_USER)
    Config.USER_TRANSMISSION = bool(
        Config.USER_TRANSMISSION and TgClient.IS_PREMIUM_USER,
    )

    if Config.AUTHORIZED_CHATS:
        aid = Config.AUTHORIZED_CHATS.split()
        for id_ in aid:
            chat_id, *thread_ids = id_.split("|")
            chat_id = int(chat_id.strip())
            if thread_ids:
                thread_ids = [int(x.strip()) for x in thread_ids]
                auth_chats[chat_id] = thread_ids
            else:
                auth_chats[chat_id] = []

    if Config.SUDO_USERS:
        aid = Config.SUDO_USERS.split()
        for id_ in aid:
            sudo_users.append(int(id_.strip()))

    if Config.EXCLUDED_EXTENSIONS:
        fx = Config.EXCLUDED_EXTENSIONS.split()
        for x in fx:
            x = x.lstrip(".")
            excluded_extensions.append(x.strip().lower())

    if Config.INCLUDED_EXTENSIONS:
        fx = Config.INCLUDED_EXTENSIONS.split()
        for x in fx:
            x = x.lstrip(".")
            included_extensions.append(x.strip().lower())

    if Config.HEROKU_APP_NAME and Config.HEROKU_API_KEY:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {Config.HEROKU_API_KEY}",
        }

        urls = [
            f"https://api.heroku.com/teams/apps/{Config.HEROKU_APP_NAME}",
            f"https://api.heroku.com/apps/{Config.HEROKU_APP_NAME}",
        ]

        async with aiohttp.ClientSession(headers=headers) as session:
            for url in urls:
                try:
                    async with session.get(url) as response:
                        response.raise_for_status()
                        app_data = await response.json()
                        if web_url := app_data.get("web_url"):
                            Config.set("BASE_URL", web_url.rstrip("/"))
                            return
                except Exception as e:
                    LOGGER.error(f"BASE_URL error: {e}")
                    continue


async def load_configurations():
    """Performs initial setup for configurations like .netrc,
    starts the Gunicorn web server.
    """

    if not await aiopath.exists(".netrc"):
        async with aiopen(".netrc", "w"):
            pass

    PORT = int(environ.get("PORT") or environ.get("BASE_URL_PORT") or "80")
    await create_subprocess_shell(
        f"gunicorn -k uvicorn.workers.UvicornWorker -w 1 web.wserver:app --bind 0.0.0.0:{PORT}",
    )
