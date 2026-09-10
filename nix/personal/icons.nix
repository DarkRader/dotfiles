{ getIcon, ... }:
{
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
}
