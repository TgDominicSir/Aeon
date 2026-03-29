# Simple YT-DLP Downloader Bot

A lightweight and efficient Telegram bot for downloading media from YouTube, TikTok, Instagram, and other yt-dlp supported sites, and uploading them directly to Telegram.

## Features

- **Fast Downloader**: Powered by `yt-dlp` for high-speed downloads.
- **Multiple Platform Support**: Download from YouTube, TikTok, Instagram, and more.
- **Direct Telegram Upload**: Files are sent directly to your Telegram chat.
- **Status Bar**: Real-time progress tracking for downloads and uploads.
- **Easy Deployment**: Ready for Heroku and VPS.

## Setup and Deployment

### Required Configuration

- `BOT_TOKEN`: Your Telegram Bot Token.
- `OWNER_ID`: Your Telegram User ID.
- `TELEGRAM_API`: Your Telegram API ID.
- `TELEGRAM_HASH`: Your Telegram API Hash.

### Optional Configuration

- `DATABASE_URL`: MongoDB URL for persisting settings.
- `LEECH_SPLIT_SIZE`: Max size for a single file (default: 2GB).
- `LEECH_DUMP_CHAT`: Chat ID where files will be dumped.

### Deployment on Heroku

1. Create a new app on Heroku.
2. Connect your GitHub repository.
3. Add the required config vars in the app settings.
4. Deploy the branch.
5. Enable the `worker` dyno.

### Deployment on VPS

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Fill the `config.py` file based on `config_sample.py`.
4. Run the bot: `python3 -m bot`.

## Usage

- `/ytdl [link]` - Download media as a video/audio based on selection.
- `/ytdlleech [link]` - Leech media directly.
- `/status` - Check current active tasks.
- `/cancel` - Cancel a task.

## Acknowledgements

- Based on [Aeon-MLTB](https://github.com/AeonOrg/Aeon-MLTB).
- Powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [Pyrogram](https://github.com/pyrogram/pyrogram).
