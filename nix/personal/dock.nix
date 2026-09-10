{ userApp, ... }:
{
  system.defaults.dock.persistent-apps = [
    (userApp "Safari")
    "/Applications/Spark Desktop.app"
    "/Applications/Obsidian.app"
    "/Applications/Notion Calendar.app"
    "/Applications/TickTick.app"
    "/Applications/Gemini.app"
    "/Applications/Discord.app"
    "/Applications/Spotify.app"
    "/Applications/Telegram.app"
    "/Applications/Zed.app"
    "/Applications/Warp.app"
  ];
}
