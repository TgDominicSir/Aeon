from asyncio import sleep
from functools import partial
from html import escape
from io import BytesIO
from os import getcwd
from time import time

from aiofiles.os import makedirs, remove
from aiofiles.os import path as aiopath
from pyrogram.filters import create
from pyrogram.handlers import MessageHandler

from bot import (
    auth_chats,
    excluded_extensions,
    included_extensions,
    sudo_users,
    user_data,
)
from bot.core.config_manager import Config
from bot.core.telegram_manager import TgClient
from bot.helper.ext_utils.bot_utils import (
    get_size_bytes,
    new_task,
    update_user_ldata,
)
from bot.helper.ext_utils.db_handler import database
from bot.helper.ext_utils.help_messages import user_settings_text
from bot.helper.ext_utils.media_utils import create_thumb
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.telegram_helper.message_utils import (
    delete_message,
    edit_message,
    send_file,
    send_message,
)

handler_dict = {}
no_thumb = "https://graph.org/file/73ae908d18c6b38038071.jpg"

leech_options = [
    "THUMBNAIL",
    "LEECH_SPLIT_SIZE",
    "LEECH_FILENAME_CAPTION",
    "THUMBNAIL_LAYOUT",
    "USER_SESSION",
]


async def get_user_settings(from_user, stype="main"):
    user_id = from_user.id
    name = from_user.mention
    buttons = ButtonMaker()
    thumbpath = f"thumbnails/{user_id}.jpg"
    user_dict = user_data.get(user_id, {})
    thumbnail = thumbpath if await aiopath.exists(thumbpath) else no_thumb

    if stype == "leech":
        buttons.data_button("thumbnail", f"userset {user_id} menu THUMBNAIL")
        buttons.data_button(
            "Leech Caption",
            f"userset {user_id} menu LEECH_FILENAME_CAPTION",
        )
        if user_dict.get("LEECH_FILENAME_CAPTION", False):
            lcap = user_dict["LEECH_FILENAME_CAPTION"]
        elif (
            "LEECH_FILENAME_CAPTION" not in user_dict
            and Config.LEECH_FILENAME_CAPTION
        ):
            lcap = Config.LEECH_FILENAME_CAPTION
        else:
            lcap = "None"

        buttons.data_button(
            "User Session",
            f"userset {user_id} menu USER_SESSION",
        )
        usess = "added" if user_dict.get("USER_SESSION", False) else "None"
        if user_dict.get("AS_DOCUMENT", False) or (
            "AS_DOCUMENT" not in user_dict and Config.AS_DOCUMENT
        ):
            ltype = "DOCUMENT"
            buttons.data_button(
                "Send As Media",
                f"userset {user_id} tog AS_DOCUMENT f",
            )
        else:
            ltype = "MEDIA"
            buttons.data_button(
                "Send As Document",
                f"userset {user_id} tog AS_DOCUMENT t",
            )
        if user_dict.get("MEDIA_GROUP", False) or (
            "MEDIA_GROUP" not in user_dict and Config.MEDIA_GROUP
        ):
            buttons.data_button(
                "Disable Media Group",
                f"userset {user_id} tog MEDIA_GROUP f",
            )
            media_group = "Enabled"
        else:
            buttons.data_button(
                "Enable Media Group",
                f"userset {user_id} tog MEDIA_GROUP t",
            )
            media_group = "Disabled"
        buttons.data_button(
            "Thumbnail Layout",
            f"userset {user_id} menu THUMBNAIL_LAYOUT",
        )
        if user_dict.get("THUMBNAIL_LAYOUT", False):
            thumb_layout = user_dict["THUMBNAIL_LAYOUT"]
        elif "THUMBNAIL_LAYOUT" not in user_dict and Config.THUMBNAIL_LAYOUT:
            thumb_layout = Config.THUMBNAIL_LAYOUT
        else:
            thumb_layout = "None"

        buttons.data_button("Back", f"userset {user_id} back")
        buttons.data_button("Close", f"userset {user_id} close")

        text = f"""<u>Leech Settings for {name}</u>
Leech Type is <b>{ltype}</b>
Media Group is <b>{media_group}</b>
Leech Caption is <code>{escape(lcap)}</code>
User session is {usess}
Thumbnail Layout is <b>{thumb_layout}</b>
"""
    elif stype == "youtube":
        buttons.data_button(
            "Default Privacy",
            f"userset {user_id} menu YT_DEFAULT_PRIVACY",
        )
        yt_privacy = user_dict.get("YT_DEFAULT_PRIVACY", "unlisted")

        buttons.data_button(
            "Default Category",
            f"userset {user_id} menu YT_DEFAULT_CATEGORY",
        )
        yt_category = user_dict.get("YT_DEFAULT_CATEGORY", "22")

        buttons.data_button(
            "Default Tags",
            f"userset {user_id} menu YT_DEFAULT_TAGS",
        )
        yt_tags = user_dict.get("YT_DEFAULT_TAGS", "None")

        buttons.data_button(
            "Default Description",
            f"userset {user_id} menu YT_DEFAULT_DESCRIPTION",
        )
        yt_description = user_dict.get(
            "YT_DEFAULT_DESCRIPTION", "Uploaded by Dominic-MLTB."
        )

        buttons.data_button(
            "Upload Mode",
            f"userset {user_id} menu YT_DEFAULT_FOLDER_MODE",
        )
        yt_folder_mode = user_dict.get("YT_DEFAULT_FOLDER_MODE", "playlist")

        buttons.data_button(
            "Add to Playlist ID",
            f"userset {user_id} menu YT_ADD_TO_PLAYLIST_ID",
        )
        yt_add_to_playlist_id = user_dict.get("YT_ADD_TO_PLAYLIST_ID", "None")

        buttons.data_button("Back", f"userset {user_id} back")
        buttons.data_button("Close", f"userset {user_id} close")
        text = f"""<u>YouTube Settings for {name}</u>
Default Privacy: <code>{yt_privacy}</code>
Default Category: <code>{yt_category}</code>
Default Tags: <code>{yt_tags}</code>
Default Description: <code>{yt_description}</code>
Default Folder Upload Mode: <b>{yt_folder_mode.capitalize()}</b>
Add to Playlist ID: <code>{yt_add_to_playlist_id}</code>"""
    elif stype == "youtube_folder_mode_menu":
        buttons.data_button(
            "Playlist", f"userset {user_id} set_yt_folder_mode playlist"
        )
        buttons.data_button(
            "Individual", f"userset {user_id} set_yt_folder_mode individual"
        )
        buttons.data_button("Back", f"userset {user_id} youtube")
        buttons.data_button("Close", f"userset {user_id} close")
        text = f"<u>Set Default YouTube Folder Upload Mode for {name}</u>"
    else:
        buttons.data_button("Leech", f"userset {user_id} leech")
        buttons.data_button("YouTube", f"userset {user_id} youtube")

        buttons.data_button(
            "Excluded Extensions",
            f"userset {user_id} menu EXCLUDED_EXTENSIONS",
        )
        if user_dict.get("EXCLUDED_EXTENSIONS", False):
            ex_ex = user_dict["EXCLUDED_EXTENSIONS"]
        elif "EXCLUDED_EXTENSIONS" not in user_dict:
            ex_ex = excluded_extensions
        else:
            ex_ex = "None"

        buttons.data_button(
            "Included Extensions", f"userset {user_id} menu INCLUDED_EXTENSIONS"
        )
        if user_dict.get("INCLUDED_EXTENSIONS", False):
            inc_ex = user_dict["INCLUDED_EXTENSIONS"]
        elif "INCLUDED_EXTENSIONS" not in user_dict:
            inc_ex = included_extensions
        else:
            inc_ex = "None"
        if user_dict.get("NAME_SUBSTITUTE", False) or (
            "NAME_SUBSTITUTE" not in user_dict and Config.NAME_SUBSTITUTE
        ):
            ns_msg = "Added"
        else:
            ns_msg = "None"
        buttons.data_button(
            "Name Substitute",
            f"userset {user_id} menu NAME_SUBSTITUTE",
        )
        if user_dict.get("NAME_PREFIX", False):
            np_msg = user_dict["NAME_PREFIX"]
        elif "NAME_PREFIX" not in user_dict:
            np_msg = excluded_extensions
        else:
            np_msg = "None"
        buttons.data_button("Name Prefix", f"userset {user_id} menu NAME_PREFIX")

        buttons.data_button(
            "YT-DLP Options",
            f"userset {user_id} menu YT_DLP_OPTIONS",
        )
        if user_dict.get("YT_DLP_OPTIONS", False):
            ytopt = user_dict["YT_DLP_OPTIONS"]
        elif "YT_DLP_OPTIONS" not in user_dict and Config.YT_DLP_OPTIONS:
            ytopt = Config.YT_DLP_OPTIONS
        else:
            ytopt = "None"

        buttons.data_button("FFmpeg Cmds", f"userset {user_id} menu FFMPEG_CMDS")
        if user_dict.get("FFMPEG_CMDS", False):
            ffc = "Added by user"
        elif "FFMPEG_CMDS" not in user_dict and Config.FFMPEG_CMDS:
            ffc = "Added by owner"
        else:
            ffc = "None"

        if user_dict:
            buttons.data_button("Reset All", f"userset {user_id} reset all")

        buttons.data_button("Close", f"userset {user_id} close")

        text = f"""<u>Settings for {name}</u>
Name substitution is <code>{ns_msg}</code>
Name prefix is <code>{np_msg}</code>
Excluded Extensions is <code>{ex_ex}</code>
Included Extensions is <code>{inc_ex}</code>
YT-DLP Options is <code>{ytopt}</code>
FFMPEG Commands is <code>{ffc}</code>"""

    return text, buttons.build_menu(2), thumbnail


async def update_user_settings(query, stype="main"):
    handler_dict[query.from_user.id] = False
    msg, button, t = await get_user_settings(query.from_user, stype)
    await edit_message(query.message, msg, button, t)


@new_task
async def send_user_settings(_, message):
    from_user = message.from_user
    handler_dict[from_user.id] = False
    msg, button, t = await get_user_settings(from_user)
    await send_message(message, msg, button, t)


@new_task
async def add_file(_, message, ftype):
    user_id = message.from_user.id
    handler_dict[user_id] = False
    if ftype == "THUMBNAIL":
        des_dir = await create_thumb(message, user_id)
    update_user_ldata(user_id, ftype, des_dir)
    await delete_message(message)
    await database.update_user_doc(user_id, ftype, des_dir)


@new_task
async def add_one(_, message, option):
    user_id = message.from_user.id
    handler_dict[user_id] = False
    user_dict = user_data.get(user_id, {})
    value = message.text
    if value.startswith("{") and value.endswith("}"):
        try:
            value = eval(value)
            if user_dict[option]:
                user_dict[option].update(value)
            else:
                update_user_ldata(user_id, option, value)
        except Exception as e:
            await send_message(message, str(e))
            return
    else:
        await send_message(message, "It must be dict!")
        return
    await delete_message(message)
    await database.update_user_data(user_id)


@new_task
async def remove_one(_, message, option):
    user_id = message.from_user.id
    handler_dict[user_id] = False
    user_dict = user_data.get(user_id, {})
    names = message.text.split("/")
    for name in names:
        if name in user_dict[option]:
            del user_dict[option][name]
    await delete_message(message)
    await database.update_user_data(user_id)


@new_task
async def set_option(_, message, option):
    user_id = message.from_user.id
    handler_dict[user_id] = False
    value = message.text
    if option == "LEECH_SPLIT_SIZE":
        if not value.isdigit():
            value = get_size_bytes(value)
        value = min(int(value), TgClient.MAX_SPLIT_SIZE)
    elif option == "EXCLUDED_EXTENSIONS":
        fx = value.split()
        value = []
        for x in fx:
            x = x.lstrip(".")
            value.append(x.strip().lower())
    elif option == "INCLUDED_EXTENSIONS":
        fx = value.split()
        value = []
        for x in fx:
            x = x.lstrip(".")
            value.append(x.strip().lower())
    elif option in ["FFMPEG_CMDS", "YT_DLP_OPTIONS"]:
        if value.startswith("{") and value.endswith("}"):
            try:
                value = eval(value)
            except Exception as e:
                await send_message(message, str(e))
                return
        else:
            await send_message(message, "It must be dict!")
            return
    update_user_ldata(user_id, option, value)
    await delete_message(message)
    await database.update_user_data(user_id)


async def get_menu(option, message, user_id):
    handler_dict[user_id] = False
    user_dict = user_data.get(user_id, {})
    buttons = ButtonMaker()
    if option in ["THUMBNAIL"]:
        key = "file"
    else:
        key = "set"
    buttons.data_button("Set", f"userset {user_id} {key} {option}")
    if option in user_dict and key != "file":
        buttons.data_button("Reset", f"userset {user_id} reset {option}")
    buttons.data_button("Remove", f"userset {user_id} remove {option}")
    if option == "FFMPEG_CMDS":
        ffc = None
        if user_dict.get("FFMPEG_CMDS", False):
            ffc = user_dict["FFMPEG_CMDS"]
            buttons.data_button("Add one", f"userset {user_id} addone {option}")
            buttons.data_button("Remove one", f"userset {user_id} rmone {option}")
        elif "FFMPEG_CMDS" not in user_dict and Config.FFMPEG_CMDS:
            ffc = Config.FFMPEG_CMDS
        if ffc:
            from re import findall
            buttons.data_button("FFMPEG VARIABLES", f"userset {user_id} ffvar")
            buttons.data_button("View", f"userset {user_id} view {option}")
    elif user_dict.get(option):
        if option == "THUMBNAIL":
            buttons.data_button("View", f"userset {user_id} view {option}")
        elif option in ["YT_DLP_OPTIONS"]:
            buttons.data_button("Add one", f"userset {user_id} addone {option}")
            buttons.data_button("Remove one", f"userset {user_id} rmone {option}")
    if option in leech_options:
        back_to = "leech"
    elif option in [
        "YT_DEFAULT_PRIVACY",
        "YT_DEFAULT_CATEGORY",
        "YT_DEFAULT_TAGS",
        "YT_DEFAULT_DESCRIPTION",
        "YT_ADD_TO_PLAYLIST_ID",
    ]:
        back_to = "youtube"
    else:
        back_to = "back"
    buttons.data_button("Back", f"userset {user_id} {back_to}")
    buttons.data_button("Close", f"userset {user_id} close")
    text = f"Edit menu for: {option}"
    await edit_message(message, text, buttons.build_menu(2))


async def set_ffmpeg_variable(_, message, key, value, index):
    user_id = message.from_user.id
    handler_dict[user_id] = False
    txt = message.text
    user_dict = user_data.setdefault(user_id, {})
    ffvar_data = user_dict.setdefault("FFMPEG_VARIABLES", {})
    ffvar_data = ffvar_data.setdefault(key, {})
    ffvar_data = ffvar_data.setdefault(index, {})
    ffvar_data[value] = txt
    await delete_message(message)
    await database.update_user_data(user_id)


async def ffmpeg_variables(
    client, query, message, user_id, key=None, value=None, index=None
):
    user_dict = user_data.get(user_id, {})
    ffc = None
    if user_dict.get("FFMPEG_CMDS", False):
        ffc = user_dict["FFMPEG_CMDS"]
    elif "FFMPEG_CMDS" not in user_dict and Config.FFMPEG_CMDS:
        ffc = Config.FFMPEG_CMDS
    if ffc:
        from re import findall
        buttons = ButtonMaker()
        if key is None:
            msg = "Choose which key you want to fill/edit variables in it:"
            for k, v in list(ffc.items()):
                add = False
                for i in v:
                    if variables := findall(r"\{(.*?)\}", i):
                        add = True
                if add:
                    buttons.data_button(k, f"userset {user_id} ffvar {k}")
            buttons.data_button("Back", f"userset {user_id} menu FFMPEG_CMDS")
            buttons.data_button("Close", f"userset {user_id} close")
        elif key in ffc and value is None:
            msg = f"Choose which variable you want to fill/edit: <u>{key}</u>\n\nCMDS:\n{ffc[key]}"
            for ind, vl in enumerate(ffc[key]):
                if variables := set(findall(r"\{(.*?)\}", vl)):
                    for var in variables:
                        buttons.data_button(
                            var, f"userset {user_id} ffvar {key} {var} {ind}"
                        )
            buttons.data_button(
                "Reset", f"userset {user_id} ffvar {key} ffmpegvarreset"
            )
            buttons.data_button("Back", f"userset {user_id} ffvar")
            buttons.data_button("Close", f"userset {user_id} close")
        elif key in ffc and value:
            old_value = (
                user_dict.get("FFMPEG_VARIABLES", {})
                .get(key, {})
                .get(index, {})
                .get(value, "")
            )
            msg = f"Edit/Fill this FFmpeg Variable: <u>{key}</u>\n\nItem: {ffc[key][int(index)]}\n\nVariable: {value}"
            if old_value:
                msg += f"\n\nCurrent Value: {old_value}"
            buttons.data_button("Back", f"userset {user_id} setevent")
            buttons.data_button("Close", f"userset {user_id} close")
        else:
            return
        await edit_message(message, msg, buttons.build_menu(2))
        if key in ffc and value:
            pfunc = partial(set_ffmpeg_variable, key=key, value=value, index=index)
            await event_handler(client, query, pfunc)
            await ffmpeg_variables(client, query, message, user_id, key)


async def event_handler(client, query, pfunc, photo=False, document=False):
    user_id = query.from_user.id
    handler_dict[user_id] = True
    start_time = time()

    async def event_filter(_, __, event):
        if photo:
            mtype = event.photo
        elif document:
            mtype = event.document
        else:
            mtype = event.text
        user = event.from_user or event.sender_chat
        return bool(
            user.id == user_id and event.chat.id == query.message.chat.id and mtype,
        )

    handler = client.add_handler(
        MessageHandler(pfunc, filters=create(event_filter)),
        group=-1,
    )

    while handler_dict[user_id]:
        await sleep(0.5)
        if time() - start_time > 60:
            handler_dict[user_id] = False
    client.remove_handler(*handler)


@new_task
async def edit_user_settings(client, query):
    from_user = query.from_user
    user_id = from_user.id
    name = from_user.mention
    message = query.message
    data = query.data.split()
    handler_dict[user_id] = False
    thumb_path = f"thumbnails/{user_id}.jpg"
    user_dict = user_data.get(user_id, {})
    if user_id != int(data[1]):
        await query.answer("Not Yours!", show_alert=True)
    elif data[2] == "setevent":
        await query.answer()
    elif data[2] in ["leech", "youtube"]:
        await query.answer()
        await update_user_settings(query, data[2])
    elif data[2] == "menu":
        await query.answer()
        if data[3] == "YT_DEFAULT_FOLDER_MODE":
            await update_user_settings(query, "youtube_folder_mode_menu")
        else:
            await get_menu(data[3], message, user_id)
    elif data[2] == "set_yt_folder_mode":
        await query.answer()
        new_mode = data[3]
        update_user_ldata(user_id, "YT_DEFAULT_FOLDER_MODE", new_mode)
        await database.update_user_data(user_id)
        await update_user_settings(query, "youtube")
    elif data[2] == "tog":
        await query.answer()
        update_user_ldata(user_id, data[3], data[4] == "t")
        await update_user_settings(query, stype="leech")
        await database.update_user_data(user_id)
    elif data[2] == "file":
        await query.answer()
        buttons = ButtonMaker()
        if data[3] == "THUMBNAIL":
            text = "Send a photo to save it as custom thumbnail. Timeout: 60 sec"
        buttons.data_button("Back", f"userset {user_id} setevent")
        buttons.data_button("Close", f"userset {user_id} close")
        await edit_message(message, text, buttons.build_menu(1))
        pfunc = partial(add_file, ftype=data[3])
        await event_handler(
            client,
            query,
            pfunc,
            photo=data[3] == "THUMBNAIL",
            document=data[3] != "THUMBNAIL",
        )
        await get_menu(data[3], message, user_id)
    elif data[2] == "ffvar":
        await query.answer()
        key = data[3] if len(data) > 3 else None
        value = data[4] if len(data) > 4 else None
        if value == "ffmpegvarreset":
            user_dict = user_data.get(user_id, {})
            ff_data = user_dict.get("FFMPEG_VARIABLES", {})
            if key in ff_data:
                del ff_data[key]
                await database.update_user_data(user_id)
            return
        index = data[5] if len(data) > 5 else None
        await ffmpeg_variables(client, query, message, user_id, key, value, index)
    elif data[2] in ["set", "addone", "rmone"]:
        await query.answer()
        buttons = ButtonMaker()
        if data[2] == "set":
            text = user_settings_text[data[3]]
            func = set_option
        elif data[2] == "addone":
            text = f"Add one or more string key and value to {data[3]}. Example: {{'key 1': 62625261, 'key 2': 'value 2'}}. Timeout: 60 sec"
            func = add_one
        elif data[2] == "rmone":
            text = f"Remove one or more key from {data[3]}. Example: key 1/key2/key 3. Timeout: 60 sec"
            func = remove_one
        buttons.data_button("Back", f"userset {user_id} setevent")
        buttons.data_button("Close", f"userset {user_id} close")
        await edit_message(message, text, buttons.build_menu(1))
        pfunc = partial(func, option=data[3])
        await event_handler(client, query, pfunc)
        await get_menu(data[3], message, user_id)
    elif data[2] == "remove":
        await query.answer("Removed!", show_alert=True)
        if data[3] in ["THUMBNAIL"]:
            fpath = thumb_path
            if await aiopath.exists(fpath):
                await remove(fpath)
            user_dict.pop(data[3], None)
            await database.update_user_doc(user_id, data[3])
        else:
            update_user_ldata(user_id, data[3], "")
            await database.update_user_data(user_id)
    elif data[2] == "reset":
        await query.answer("Reseted!", show_alert=True)
        if data[3] in user_dict:
            user_dict.pop(data[3], None)
        else:
            for k in list(user_dict.keys()):
                if k not in [
                    "SUDO",
                    "AUTH",
                    "THUMBNAIL",
                ]:
                    del user_dict[k]
            await update_user_settings(query)
        await database.update_user_data(user_id)
    elif data[2] == "view":
        await query.answer()
        if data[3] == "THUMBNAIL":
            await send_file(message, thumb_path, name)
        elif data[3] == "FFMPEG_CMDS":
            ffc = None
            if user_dict.get("FFMPEG_CMDS", False):
                ffc = user_dict["FFMPEG_CMDS"]
            elif "FFMPEG_CMDS" not in user_dict and Config.FFMPEG_CMDS:
                ffc = Config.FFMPEG_CMDS
            msg_ecd = str(ffc).encode()
            with BytesIO(msg_ecd) as ofile:
                ofile.name = "users_settings.txt"
                await send_file(message, ofile)
    elif data[2] == "back":
        await query.answer()
        await update_user_settings(query)
    else:
        await query.answer()
        await delete_message(message.reply_to_message)
        await delete_message(message)


@new_task
async def get_users_settings(_, message):
    msg = ""
    if auth_chats:
        msg += f"AUTHORIZED_CHATS: {auth_chats}\n"
    if sudo_users:
        msg += f"SUDO_USERS: {sudo_users}\n\n"
    if user_data:
        for u, d in user_data.items():
            kmsg = f"\n<b>{u}:</b>\n"
            if vmsg := "".join(
                f"{k}: <code>{v or None}</code>\n" for k, v in d.items()
            ):
                msg += kmsg + vmsg
        if not msg:
            await send_message(message, "No users data!")
            return
        msg_ecd = msg.encode()
        if len(msg_ecd) > 4000:
            with BytesIO(msg_ecd) as ofile:
                ofile.name = "users_settings.txt"
                await send_file(message, ofile)
        else:
            await send_message(message, msg)
    else:
        await send_message(message, "No users data!")
