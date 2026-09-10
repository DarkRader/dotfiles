{ pkgs, getIcon, userApp, ... }:
{
  theme.icons = "light";

  environment.systemPackages = [
    pkgs.cloudflared
    pkgs.codex-acp
  ];

  environment.customIcons.icons = [
    {
      path = "/Applications/Discord.app";
      icon = getIcon "discord";
    }
    {
      path = "/Applications/Gemini.app";
      icon = getIcon "gemini";
    }
  ];

  system.defaults = {
    dock = {
      persistent-apps = [
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
    };
  };

  homebrew = {
    brews = [
      "kubernetes-cli"
      "wireguard-tools"
      "yt-dlp"
    ];
    casks = [
      "iina"
    ];
    masApps = {
      # "Pages" = 361309726;
      # "Numbers" = 361304891;
      # "Goodnotes" = 1444383602;
    };
  };
}
