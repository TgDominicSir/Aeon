# Simple YT-DLP Downloader Bot

A lightweight and efficient Telegram bot for downloading media from YouTube, TikTok, Instagram, and other yt-dlp supported sites, and uploading them directly to Telegram.

## Features

- **Fast Downloader**: Powered by `yt-dlp` for high-speed downloads.
- **Universal Access**: Works for everyone in Private Messages and in any group where the bot is an admin.
- **Real-time Status**: Follow your downloads with a sleek progress bar.
- **Customizable**: Change settings like maximum concurrent tasks (default: 12) on the fly.
- **Easy Deployment**: Fully compatible with Heroku and VPS.

## User Settings

Users can customize their experience using the `/settings` command:

- **LEECH_SPLIT_SIZE**: Set the maximum size for a single file (e.g., 2GB).
- **AS_DOCUMENT**: Choose to receive files as documents instead of media.
- **MEDIA_GROUP**: Send multiple files from a single link as a media group.
- **NAME_PREFIX**: Add a custom prefix to all downloaded files.
- **THUMBNAIL**: Upload a custom thumbnail for your downloads.

## Supported Sites

This bot supports all sites compatible with `yt-dlp`, including:

- **YouTube**: Videos, Shorts, Playlists.
- **TikTok**: Videos (with/without watermark).
- **Instagram**: Reels, IGTV, Posts.
- **Twitter/X**: Videos.
- **Facebook**: Public videos.
- **SoundCloud**: Audio tracks.
- **And 1000+ more!** [Full list here](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

## Setup and Deployment

### Required Configuration

- `BOT_TOKEN`: Your Telegram Bot Token.
- `OWNER_ID`: Your Telegram User ID.
- `TELEGRAM_API`: Your Telegram API ID.
- `TELEGRAM_HASH`: Your Telegram API Hash.

### Optional Configuration

- `DATABASE_URL`: MongoDB URL for persisting settings and custom thumbnails.
- `QUEUE_ALL`: Maximum concurrent tasks bot-wide (default: 12).
- `LEECH_DUMP_CHAT`: Chat ID where all downloads will be logged/backed up.

### Deployment on Heroku

1. Create a new app on Heroku.
2. Connect your GitHub repository.
3. Add the required config vars in the app settings.
4. Deploy the branch.
5. Enable the `worker` dyno.

### Deployment on VPS

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Create a `config.py` file or set Environment Variables.
4. Run the bot: `python3 -m bot`.

## Usage

- `/ytdl [link]` - Download media with format selection (Video/Audio/Quality).
- `/ytdlleech [link]` - Download the best available quality directly.
- `/status` - View all active downloads and bot performance.
- `/settings` - Access your personal download settings.
- `/cancel` - Stop an ongoing task.

## Admin Commands (Owner/Sudo Only)

- `/botsettings` - Configure bot-wide limits and variables.
- `/stats` - Detailed system and bot statistics.
- `/restart` - Reboot the bot instance.
- `/log` - View recent bot logs.

## Acknowledgements

- Refactored from [Aeon-MLTB](https://github.com/AeonOrg/Aeon-MLTB).
- Core powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [Pyrogram](https://github.com/pyrogram/pyrogram).
