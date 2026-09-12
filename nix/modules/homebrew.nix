{ ... }:
{
  homebrew = {
    enable = true;

    onActivation = {
      autoUpdate = true;
      upgrade = true;
      cleanup = "zap";
    };

    taps = [
      "hashicorp/tap"
      "DarkRader/tap"
    ];

    # Infrastructure tools
    brews = [
      "hashicorp/tap/terraform"
      "hashicorp/tap/vault"
      "DarkRader/tap/macicon"
    ];

    # Desktop applications
    casks = [
      "antigravity-cli"
      "appcleaner"
      "claude"
      "codex"
      "font-jetbrains-mono-nerd-font"
      "hiddenbar"
      "obsidian"
      "orbstack"
      "postman"
      "postman-agent"
      "raycast"
      "readdle-spark"
      "spotify"
      "warp"
      "zed"
      "telegram"
      "notion-calendar"
      "ticktick"
    ];
  };
}
