{ pkgs, ... }:
{
  environment.systemPackages = [
    pkgs.neovim
  ];

  system.stateVersion = 6;
  nixpkgs.hostPlatform = "aarch64-darwin";

  nix.settings.experimental-features = "nix-command flakes";

  homebrew = {
    enable = true;

    onActivation = {
      autoUpdate = false;
      upgrade = false;
      cleanup = "none";
    };

    taps = [
      "anomalyco/tap"
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
      "go"
      "helm"
      "htop"
      "jpeg-xl"
      "kind"
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
      "anomalyco/tap/opencode"
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
      "claude-code"
      "codex"
      "font-jetbrains-mono-nerd-font"
      "gcloud-cli"
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
