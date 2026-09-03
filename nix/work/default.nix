{ ... }:
{
  system.defaults = {
    dock = {
      persistent-apps = [
        "/Applications/Safari.app"
        "/Applications/Spark Desktop.app"
        "/Applications/Obsidian.app"
        "/Applications/Notion.app"
        "/Applications/Notion Calendar.app"
        "/Applications/TickTick.app"
        "/Applications/Claude.app"
        "/Applications/Microsoft Teams.app"
        "/Applications/Spotify.app"
        "/Applications/Slack.app"
        "/Applications/Telegram.app"
        "/Applications/Zed.app"
        "/Applications/Warp.app"
        "/System/Applications/App Store.app"
        "/System/Applications/System Settings.app"
      ];
    };
  };

  homebrew.brews = [
    "azure-cli"
    "poetry"
    "pgloader"
    "pulumi"
  ];

  homebrew.casks = [
    "slack"
    "microsoft-teams"
    "notion"
    "claude"
    "gcloud-cli"
    "bitwarden"
  ];
}
