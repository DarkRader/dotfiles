# Zsh
alias zshrc="$EDITOR ~/.zshrc"
alias ohmyzsh="$EDITOR ~/.oh-my-zsh"
alias zshreload="source ~/.zshrc && clear"

# Terminal
alias cls="clear && ls"
alias ed="$EDITOR"
alias dot="$HOME/dotfiles"
alias ls="eza --icons --group-directories-first"
alias catal="cat ~/dotfiles/.zsh/aliases.zsh"
alias darwin-personal="darwin-switch personal"
alias darwin-work="darwin-switch work"

# Git aliases
alias ga="git add"
alias gc="git commit -m"
alias gs="git status"
alias gsw="git switch"
alias gp="git push"
alias gl="git log"
alias gll="git log --oneline --graph --all --decorate"

# Docker
alias dco="docker compose"
alias dcolog="docker compose logs"
alias dps="docker ps"
alias dpa="docker ps -a"
alias dl="docker ps -l -q"
alias dx="docker exec -it"

# Reposities
alias cloudrader="cd ~/Git/CloudRader"
alias reservium-api="cd ~/Git/CloudRader/reservium-api/"
alias reservium-ui="cd ~/Git/CloudRader/reservium-ui/"
alias darkrader="cd ~/Git/DarkRader"
alias dotfiles="cd ~/dotfiles"

# Tools
alias k="kubectl"
alias tf="terraform"
