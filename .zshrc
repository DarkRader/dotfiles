# p10k enable
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# ---------------------------------------------------------------------------------------
# ----------------------Z-S-H---C-O-N-F-I-G----------------------------------------------
# ---------------------------------------------------------------------------------------

#clear another string in terminal
clear
#Greeting
echo "                           WELCOME TO TERMINAL"
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
EDITOR="nano"

# ZSH Settings
ZSH_THEME="powerlevel10k/powerlevel10k"
ZSH_COLORIZE_TOOL="pygmentize"
ZSH_DISABLE_COMPFIX="true"
POWERLEVEL9K_MODE="nerdfont-complete"
export ZSH="$HOME/.oh-my-zsh"
#export JAVA_HOME="$(/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home)"

# PLUGINS
plugins=(git colorize colored-man-pages zsh-syntax-highlighting command-not-found)

# Running Oh My Zsh
source $ZSH/oh-my-zsh.sh

# Greeting
# echo "🕑 $(date +"%Y.%m.%d %T")"
# echo

# PATH
export JAVA_HOME="/usr/lib64/jvm/java-1.8.0-openjdk-1.8.0/jre"
export PATH=$PATH:/usr/sbin:~/.local/bin

# ALIASES
source $HOME/.aliases

# ---------------------------------------------------------------------------------------
# --------------E-N-D---Z-S-H---C-O-N-F-I-G----------------------------------------------
# ---------------------------------------------------------------------------------------

# p10k ending
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

source /Users/Artyom_1/.docker/init-zsh.sh || true # Added by Docker Desktop

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
export PATH="/Applications/Visual Studio Code.app/Contents/Resources/app/bin:$PATH"
export PATH="$HOME/.local/python-3.13.3-tk/bin:$PATH"
