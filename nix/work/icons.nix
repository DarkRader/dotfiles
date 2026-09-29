{ getIcon, ... }:
{
  environment.customIcons.icons = [
    {
      path = "/Applications/Slack.app";
      icon = getIcon "slack";
    }
    {
      path = "/Applications/Microsoft Teams.app";
      icon = getIcon "microsoftteams";
    }
    {
      path = "/Applications/Claude.app";
      icon = getIcon "claude";
    }
  ];
}
