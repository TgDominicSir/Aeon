from pyrogram.filters import create

from bot import sudo_users, user_data
from bot.core.config_manager import Config


class CustomFilters:
    async def owner_filter(self, _, update):
        user = update.from_user or update.sender_chat
        return user.id == Config.OWNER_ID

    owner = create(owner_filter)

    async def authorized_user(self, _, update):
        # Allow everyone in PM and groups
        return True

    authorized = create(authorized_user)

    async def sudo_user(self, _, update):
        user = update.from_user or update.sender_chat
        uid = user.id
        return bool(
            uid == Config.OWNER_ID
            or (uid in user_data and user_data[uid].get("SUDO"))
            or uid in sudo_users,
        )

    sudo = create(sudo_user)
