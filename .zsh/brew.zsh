# Wrap the brew command to auto-update the Brewfile on installs/uninstalls
brew() {
  # Run the actual brew command first
  command brew "$@"
  
  # Check if the command was an install, cask install, or uninstall
  if [[ "$1" == "install" || "$1" == "uninstall" || "$1" == "tap" || "$1" == "untap" ]]; then
    # Only update if the command succeeded
    if [ $? -eq 0 ]; then
      echo "Updating Dotfiles Brewfile..."
      # Adjust the path below to match where your dotfiles repo actually lives
      command brew bundle dump --force --file="~/.Brewfile"
    fi
  fi
}