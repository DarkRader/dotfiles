# ---------------------------------------------------------------------------------------
# ----------------------Z-S-H---C-O-N-F-I-G----------------------------------------------
# ---------------------------------------------------------------------------------------

#clear another string in terminal
clear

# Colors
BLACK='\033[0;30m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
WHITE='\033[0;36m'
CEND='\033[0m' # No color (default text color)

# Vars
EDITOR="nvim"

# ZSH Settings
ZSH_COLORIZE_TOOL="pygmentize"
ZSH_DISABLE_COMPFIX="true"
export ZSH="$HOME/.oh-my-zsh"

# PLUGINS
plugins=(git colorize colored-man-pages zsh-syntax-highlighting command-not-found)

# The old Intel Homebrew completion path may remain after migrating Homebrew
# to Nix. Keep it out of fpath unless its brew completion file exists.
if [[ ! -f /usr/local/share/zsh/site-functions/_brew ]]; then
  fpath=(${fpath:#/usr/local/share/zsh/site-functions})
fi

# Running Oh My Zsh
[[ -f "$ZSH/oh-my-zsh.sh" ]] && source "$ZSH/oh-my-zsh.sh"

echo

[[ -f ~/.zsh/starship.zsh ]] && source ~/.zsh/starship.zsh

# ALIASES
[[ -f ~/.zsh/aliases.zsh ]] && source ~/.zsh/aliases.zsh
[[ -f ~/.zsh/darwin-switch.zsh ]] && source ~/.zsh/darwin-switch.zsh

# Load Starship
eval "$(starship init zsh)"

# ---------------------------------------------------------------------------------------
# --------------E-N-D---Z-S-H---C-O-N-F-I-G----------------------------------------------
# ---------------------------------------------------------------------------------------

export PATH="$HOME/.local/python-3.13.3-tk/bin:$PATH"

export PATH="$HOME/.local/bin:$PATH"
