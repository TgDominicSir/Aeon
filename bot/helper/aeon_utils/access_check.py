from re import IGNORECASE, escape, search

from bot.helper.ext_utils.help_messages import nsfw_keywords


async def error_check(message):
    """
    Performs access checks for a message.
    Currently only checks for NSFW content as the bot is open to everyone.
    """
    msg, button = [], None

    if await nsfw_precheck(message):
        msg.append("NSFW detected")

    if msg:
        username = message.from_user.username
        tag = f"@{username}" if username else message.from_user.mention
        final_msg = f"Hey, <b>{tag}</b>!\n"
        for i, m in enumerate(msg, 1):
            final_msg += f"\n<blockquote><b>{i}</b>: {m}</blockquote>"

        if button:
            button = button.build_menu(2)
        return final_msg, button

    return None, None


def is_nsfw(text):
    pattern = (
        r"(?:^|\W|_)(?:"
        + "|".join(escape(keyword) for keyword in nsfw_keywords)
        + r")(?:$|\W|_)"
    )
    return bool(search(pattern, text, flags=IGNORECASE))


async def nsfw_precheck(message):
    if is_nsfw(message.text or ""):
        return True

    reply_to = message.reply_to_message
    if not reply_to:
        return False

    for attr in ["document", "video"]:
        if hasattr(reply_to, attr) and getattr(reply_to, attr):
            file_name = getattr(reply_to, attr).file_name
            if file_name and is_nsfw(file_name):
                return True

    return any(
        is_nsfw(getattr(reply_to, attr) or "")
        for attr in ["caption", "text"]
        if hasattr(reply_to, attr) and getattr(reply_to, attr)
    )
