# Keep Homebrew dependencies in a shared Brewfile or a personal/work overlay.
# Set BREWFILE_PROFILE to avoid the prompt, for example:
#   BREWFILE_PROFILE=work brew install --cask slack

BREWFILE_DIR="${DOTFILES_DIR:-$HOME/dotfiles}/brewfiles"

_brewfile_path() {
  case "$1" in
    shared)   print -r -- "$BREWFILE_DIR/.brewfile" ;;
    personal) print -r -- "$BREWFILE_DIR/.brewfile.personal" ;;
    work)     print -r -- "$BREWFILE_DIR/.brewfile.work" ;;
    *)
      print -u2 "Unknown Brewfile profile: $1"
      return 1
      ;;
  esac
}

_brewfile_choose_profile() {
  local profile reply

  if [[ -n "$BREWFILE_PROFILE" && "$1" != force ]]; then
    _brewfile_path "$BREWFILE_PROFILE"
    return $?
  fi

  if [[ ! -t 0 || ! -t 1 ]]; then
    _brewfile_path shared
    return
  fi

  print "Select the Brewfile to update:"
  print "  1) shared (default)"
  print "  2) personal"
  print "  3) work"
  read "reply?Profile [1]: "
  reply="${reply:-1}"

  case "$reply" in
    1|shared)   profile=shared ;;
    2|personal) profile=personal ;;
    3|work)      profile=work ;;
    *)
      print -u2 "Invalid profile; using shared."
      profile=shared
      ;;
  esac

  _brewfile_path "$profile"
}

_brewfile_packages() {
  local arg
  for arg in "$@"; do
    [[ "$arg" == -* ]] && continue
    print -r -- "$arg"
  done
}

_brewfile_record() {
  local operation="$1"
  local kind="$2"
  shift 2

  local file package
  file="$(_brewfile_choose_profile)" || return 1

  for package in "$@"; do
    command brew bundle "$operation" --file="$file" "$kind" "$package" >/dev/null || {
      print -u2 "Could not update $file for $package"
      return 1
    }
  done

  print "Updated $file"
}

# Select a profile for subsequent commands in the current shell.
# `brew profile` with no argument shows the same menu used by auto-recording.
brew() {
  if [[ "$1" == profile ]]; then
    if [[ "$2" == clear ]]; then
      unset BREWFILE_PROFILE
      print "Brewfile profile cleared; the next change will ask."
      return 0
    fi

    if [[ -n "$2" ]]; then
      _brewfile_path "$2" >/dev/null || return 1
      export BREWFILE_PROFILE="$2"
    else
      local selected
      selected="$(_brewfile_choose_profile force)" || return 1
      export BREWFILE_PROFILE=shared
      [[ "$selected" != "$BREWFILE_DIR/.brewfile" ]] && export BREWFILE_PROFILE="${selected##*.brewfile.}"
    fi

    print "Brewfile profile: $BREWFILE_PROFILE"
    return 0
  fi

  command brew "$@"
  local brew_status=$?
  (( brew_status != 0 )) && return $brew_status

  local kind
  local -a packages

  case "$1" in
    install)
      kind=--formula
      [[ " $* " == *" --cask "* ]] && kind=--cask
      packages=( ${(f)$(_brewfile_packages "$@[2,-1]")} )
      (( ${#packages} )) && _brewfile_record add "$kind" "${packages[@]}"
      ;;
    uninstall)
      kind=--formula
      [[ " $* " == *" --cask "* ]] && kind=--cask
      packages=( ${(f)$(_brewfile_packages "$@[2,-1]")} )
      (( ${#packages} )) && _brewfile_record remove "$kind" "${packages[@]}"
      ;;
    tap)
      packages=( ${(f)$(_brewfile_packages "$@[2,-1]")} )
      (( ${#packages} )) && _brewfile_record add --tap "${packages[@]}"
      ;;
    untap)
      packages=( ${(f)$(_brewfile_packages "$@[2,-1]")} )
      (( ${#packages} )) && _brewfile_record remove --tap "${packages[@]}"
      ;;
  esac

  return 0
}
