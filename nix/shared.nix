{ ... }:
{
  imports = [
    ./modules/theme.nix
    ./modules/wrappers.nix
    ./modules/icons.nix
    ./modules/defaults.nix
    ./modules/homebrew.nix
    ./modules/packages.nix
    ./modules/login-items.nix
  ];

  system.stateVersion = 6;
  nixpkgs.hostPlatform = "aarch64-darwin";

  # Determinate Nix manages the daemon and nix.conf
  nix.enable = false;
}
