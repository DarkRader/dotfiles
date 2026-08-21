{ ... }:
{
  # Profile-specific settings can be added here.
  system.defaults = {
    dock = {
      persistent-apps = [
        "/Applications/Safari.app"
        "/Applications/Spark Desktop.app"
        "/Applications/Obsidian.app"
        "/Applications/Notion.app"
        "/Applications/Notion Calendar.app"
        "/Applications/TickTick.app"
        "/Applications/ChatGPT.app"
        "/Applications/Discord.app"
        "/Applications/Spotify.app"
        "/Applications/Telegram.app"
        "/Applications/Zed.app"
        "/Applications/Warp.app"
        "/System/Applications/App Store.app"
      ];
    };
  };

  homebrew.brews = [
    "wireguard-tools"
    "yt-dlp"
  ];

  homebrew.casks = [
    "iina"
  ];
}
