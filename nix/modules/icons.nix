{ getIcon, userApp, ... }:
{
  environment.customIcons = {
    enable = true;
    icons = [
      {
        path = userApp "Safari";
        icon = getIcon "safari";
      }
      {
        path = "/Applications/Spark Desktop.app";
        icon = getIcon "spark";
      }
      {
        path = "/Applications/Obsidian.app";
        icon = getIcon "obsidian";
      }
      {
        path = "/Applications/Spotify.app";
        icon = getIcon "spotify";
      }
      {
        path = "/Applications/Telegram.app";
        icon = getIcon "telegram";
      }
      {
        path = "/Applications/Zed.app";
        icon = getIcon "zed";
      }
      {
        path = "/Applications/Warp.app";
        icon = getIcon "warp";
      }
      {
        path = "/Applications/TickTick.app";
        icon = getIcon "ticktick";
      }
      {
        path = "/Applications/Notion Calendar.app";
        icon = getIcon "notion-calendar";
      }
    ];
  };
}
