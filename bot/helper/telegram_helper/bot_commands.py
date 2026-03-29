# ruff: noqa: RUF012
from bot.core.config_manager import Config

i = Config.CMD_SUFFIX


class BotCommands:
    StartCommand = "start"
    YtdlCommand = [f"ytdl{i}", f"y{i}"]
    YtdlLeechCommand = [f"ytdlleech{i}", f"yl{i}"]
    MediaInfoCommand = f"mediainfo{i}"
    CancelAllCommand = f"cancelall{i}"
    ForceStartCommand = [f"forcestart{i}", f"fs{i}"]
    StatusCommand = [f"status{i}", "statusall"]
    UsersCommand = f"users{i}"
    AuthorizeCommand = f"auth{i}"
    UnAuthorizeCommand = f"unauth{i}"
    AddSudoCommand = f"addsudo{i}"
    RmSudoCommand = f"rmsudo{i}"
    PingCommand = f"ping{i}"
    RestartCommand = [f"restart{i}", "restartall"]
    StatsCommand = f"stats{i}"
    HelpCommand = f"help{i}"
    LogCommand = f"log{i}"
    ShellCommand = f"shell{i}"
    AExecCommand = f"aexec{i}"
    ExecCommand = f"exec{i}"
    ClearLocalsCommand = f"clearlocals{i}"
    BotSetCommand = f"botsettings{i}"
    UserSetCommand = f"settings{i}"
    SpeedTest = f"speedtest{i}"
    BroadcastCommand = [f"broadcast{i}", "broadcastall"]
