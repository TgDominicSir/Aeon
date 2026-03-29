# REQUIRED CONFIG
BOT_TOKEN = ""
OWNER_ID = 0
TELEGRAM_API = 0
TELEGRAM_HASH = ""

# Recommended for persisting settings, RSS feeds, and task history. Essential for some features.
DATABASE_URL = ""

# OPTIONAL CONFIG
TG_PROXY = {}  # Example: {"scheme": "socks5", "hostname": "11.22.33.44", "port": 1234, "username": "user", "password": "pass"}
USER_SESSION_STRING = ""
CMD_SUFFIX = ""  # Suffix to add to all bot commands
AUTHORIZED_CHATS = ""  # Space separated chat_id/user_id to authorize
SUDO_USERS = ""  # Space separated user_id for sudo access
EXCLUDED_EXTENSIONS = (
    ""  # Space separated file extensions to exclude (e.g., .log .exe)
)
INCLUDED_EXTENSIONS = ""
INCOMPLETE_TASK_NOTIFIER = (
    False  # Notify for incomplete tasks on restart (requires DATABASE_URL)
)
YT_DLP_OPTIONS = {}  # Dictionary of yt-dlp options, e.g., {"format": "bestvideo+bestaudio/best"}
NAME_SUBSTITUTE = r""  # Replace/remove words: "source1/target1|source2/target2"
FFMPEG_CMDS = {}  # Predefined FFmpeg commands, e.g., {"preset_name": ["-vf", "scale=1280:-1"]}
UPLOAD_PATHS = {}  # Named upload paths, e.g., {"movies": "remote:movies/", "tv": "gdrive_id_tv_folder"}

# Specific Features / Customizations
DELETE_LINKS = False  # Auto-delete links after a certain period or action
FSUB_IDS = ""  # Forced subscription channel IDs (comma-separated)
TOKEN_TIMEOUT = 0  # Timeout in seconds for user tokens (0 for no timeout)
PAID_CHANNEL_ID = 0  # Channel ID users must join to bypass token
PAID_CHANNEL_LINK = ""  # Invite link for the paid channel
SET_COMMANDS = True  # Register bot commands with BotFather on startup
METADATA_KEY = ""  # Key for tagging/fetching metadata
WATERMARK_KEY = ""  # Key for watermarking files
LOG_CHAT_ID = 0  # Chat ID for sending leech logs
LEECH_FILENAME_CAPTION = ""  # Template caption for leeched files
NAME_PREFIX = ""

# Update
UPSTREAM_REPO = (
    "https://github.com/AeonOrg/Aeon-MLTB"  # Upstream repository for updates
)
UPSTREAM_BRANCH = "main"  # Default branch for updates

# Leech
LEECH_SPLIT_SIZE = 2097152000  # Split size for leeched files in bytes. Default: 2GB. Max: 4GB for Premium, 2GB for others. 0 for bot default.
AS_DOCUMENT = False  # Upload leeched files as documents instead of media
MEDIA_GROUP = False  # Send leeched files as a media group
USER_TRANSMISSION = False  # Use user session for uploads/downloads (Premium only)
HYBRID_LEECH = (
    False  # Switch between bot/user session based on file size (Premium only)
)
LEECH_DUMP_CHAT = []  # List of chat_ids or channel_ids to dump leeched files, e.g., [-100123456789, "channel_username"]
THUMBNAIL_LAYOUT = ""  # Thumbnail layout for uploads (e.g., 2x2, 3x3)

# Queueing system
QUEUE_ALL = 0  # Max concurrent tasks (upload + download)
QUEUE_DOWNLOAD = 0  # Max concurrent download tasks
QUEUE_UPLOAD = 0  # Max concurrent upload tasks

# Heroku config for get BASE_URL automatically
HEROKU_APP_NAME = ""  # Name of your Heroku app, used to get BASE_URL automatically
HEROKU_API_KEY = ""  # API key for your Heroku account
