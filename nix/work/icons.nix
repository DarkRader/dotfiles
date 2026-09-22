{ getIcon, ... }:
{
  environment.customIcons.icons = [
    {
      path = "/Applications/Slack.app";
      icon = getIcon "slack";
    }
    {
      path = "/Applications/Microsoft Teams.app";
      icon = getIcon "microsoft-teams";
    }
    {
      path = "/Applications/Claude.app";
      icon = getIcon "claude";
    }
  ];
}
