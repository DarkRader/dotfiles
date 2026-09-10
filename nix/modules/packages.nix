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
}
