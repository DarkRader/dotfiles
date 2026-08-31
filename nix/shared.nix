{ pkgs, ... }:
{
  environment.systemPackages = [
    # Editor
    pkgs.neovim

    # Core CLI and repository tools
    pkgs.git
    pkgs.gh
    pkgs.stow

    # Shell and terminal
    pkgs.starship
    pkgs.eza
    pkgs.tmux
    pkgs.zsh-syntax-highlighting

    # Languages and package managers
    pkgs.python313Packages.pygments
    pkgs.pnpm
    pkgs.nodejs
    pkgs.uv

    # Development tools
    pkgs.nixd
    pkgs.nil
    pkgs.mas
    pkgs.pre-commit
    pkgs.skills

    # Media and system tools
    pkgs.ffmpeg
    pkgs.htop
  ];

  system.stateVersion = 6;
  nixpkgs.hostPlatform = "aarch64-darwin";

  nix.settings.experimental-features = "nix-command flakes";

  system.defaults = {
    NSGlobalDomain = {
      AppleInterfaceStyle = "Dark";
      # Finder sidebar icon size:
      # 1 = small, 2 = medium, 3 = large
      NSTableViewDefaultSizeMode = 2;
    };

    dock = {
      magnification = true;
      mineffect = "scale";
      minimize-to-application = true;
      autohide = true;
      show-recents = false;
    };

    finder = {
      FXPreferredViewStyle = "clmv";
      _FXSortFoldersFirst = true;
      NewWindowTarget = "Home";
      AppleShowAllExtensions = true;
    };

    trackpad = {
      Clicking = true;
      TrackpadRightClick = true;
    };

    CustomUserPreferences = {
      "com.apple.assistant.support" = {
        "Assistant Enabled" = false;
      };
      "com.apple.assistant.backedup" = {
        "Assistant Enabled" = false;
      };
      "com.apple.Siri" = {
        "StatusMenuVisible" = false;
        "UserHasDeclinedEnable" = true;
      };
    };
  };

  homebrew = {
    enable = true;

    onActivation = {
      autoUpdate = true;
      upgrade = true;
      cleanup = "zap";
    };

    taps = [
      "hashicorp/tap"
    ];

    # Infrastructure tools
    brews = [
      "hashicorp/tap/terraform"
      "hashicorp/tap/vault"
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
