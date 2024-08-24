
export alias core-ls = ls
export def old-ls [path] {
  core-ls $path | sort-by type name -i
}
export def ls [path?] {
  if $path == null {
    old-ls .
  } else {
    old-ls $path
  }
}

# git
export def gc  [args] { git add .; git commit -m $args; git push }


# fzf
export alias _fzf = fzf --prompt 'All> ' --height=90% --layout=reverse --info=inline --border --margin=1 --padding=1
export alias fzf = _fzf --preview 'bat --color=always --style=header,grid --line-range :500 {}'
export def f [query] { fzf --query $query }

# Modern unix
export alias grep = rg
export alias df = duf
export alias cat = bat
export alias dig = dog

# python virtualenv
export alias py = python

# uv
export alias activate = .venv\Scripts\activate
export alias deactivate = .venv\Scripts\deactivate


# nushell
export alias proj = cd $env.PROJECTS
export alias dot = cd $env.DOTFILES
export alias sp = cd $env.SP
export alias spu = cd $env.SP_USER
export alias spd = cd $env.SP_DATA
