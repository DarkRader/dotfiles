{ pkgs, ... }:
{
  environment.systemPackages = [
    pkgs.neovim
  ];

  system.stateVersion = 6;
  nixpkgs.hostPlatform = "aarch64-darwin";

  nix.settings.experimental-features = "nix-command flakes";

  system.defaults = {
    # NSGlobalDomain = {
    #   AppleInterfaceStyle = "Dark";
    #   AppleShowAllExtensions = true;
    #   KeyRepeat = 2;
    #   InitialKeyRepeat = 15;
    #   NSAutomaticCapitalizationEnabled = false;
    # };

    dock = {
      autohide = true;
      # show-recents = false;
      # orientation = "bottom";
    };

    # finder = {
    #   AppleShowAllExtensions = true;
    #   FXPreferredViewStyle = "clmv";
    #   ShowPathbar = true;
    #   ShowStatusBar = true;
    # };

    # trackpad = {
    #   Clicking = true;
    #   TrackpadRightClick = true;
    # };
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

    brews = [
      "certifi"
      "openssl@3"
      "zstd"
      "ansible"
      "aom"
      "cloudflared"
      "codex-acp"
      "webp"
      "little-cms2"
      "eza"
      "ffmpeg"
      "gh"
      "git"
      "gnutls"
      "htop"
      "jpeg-xl"
      "kubernetes-cli"
      "leptonica"
      "libnghttp3"
      "libngtcp2"
      "node"
      "pnpm"
      "pre-commit"
      "starship"
      "stow"
      "tesseract"
      "unbound"
      "uv"
      "wget"
      "zsh-syntax-highlighting"
      "hashicorp/tap/terraform"
      "hashicorp/tap/vault"
      "tmux"
      "npm"
      "skills"
    ];

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
