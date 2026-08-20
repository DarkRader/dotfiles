# Select and activate a nix-darwin profile.
darwin-switch() {
  local profile="$1"
  local choice

  if [[ -z "$profile" ]]; then
    print "Select nix-darwin profile:"
    select choice in personal work; do
      profile="$choice"
      break
    done
  fi

  case "$profile" in
    personal|work) ;;
    *)
      print -u2 "Usage: darwin-switch [personal|work]"
      return 2
      ;;
  esac

  sudo -H darwin-rebuild switch \
    --flake "$HOME/dotfiles/nix#macbook-$profile"
}

alias darwin-personal="darwin-switch personal"
alias darwin-work="darwin-switch work"
