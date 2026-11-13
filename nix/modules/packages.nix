{ pkgs, getIcon, ... }:
let
  alacrittyWithCustomIcon = pkgs.runCommand "alacritty-${pkgs.alacritty.version}" {
    meta = pkgs.alacritty.meta // {
      mainProgram = "alacritty";
    };
  } ''
    mkdir -p $out
    cp -PR ${pkgs.alacritty}/* $out/
    chmod -R u+w $out/Applications/Alacritty.app
    cp ${getIcon "alacritty"} $out/Applications/Alacritty.app/Contents/Resources/alacritty.icns
  '';
in
{
  environment.systemPackages = [
    # Editor
    pkgs.neovim

    # Core CLI and repository tools
    pkgs.git
    pkgs.gh

    # Shell and terminal
    alacrittyWithCustomIcon
    pkgs.oh-my-zsh
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
    pkgs.pre-commit
    pkgs.skills
    pkgs.mise

    # Media and system tools
    pkgs.ffmpeg
  ];

  system.activationScripts.postActivation.text = ''
    # Touch Nix Apps trampolines so macOS Dock invalidates its icon cache
    for app in /Applications/Nix\ Apps/*.app; do
      if [ -e "$app" ]; then
        touch "$app"
      fi
    done
  '';
}
