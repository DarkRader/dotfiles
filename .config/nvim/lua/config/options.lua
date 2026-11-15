local opt = vim.opt

-- Line numbers
opt.number = true
opt.relativenumber = true

-- Tabs & Indentation (2 spaces)
opt.tabstop = 2
opt.shiftwidth = 2
opt.expandtab = true
opt.autoindent = true
opt.smartindent = true

-- Appearance & Colors
opt.termguicolors = true
opt.signcolumn = "yes"
opt.cursorline = true
opt.showmode = false -- Handled by lualine

-- Search settings
opt.ignorecase = true
opt.smartcase = true
opt.hlsearch = true
opt.incsearch = true

-- Clipboard & Mouse
opt.clipboard = "unnamedplus" -- Sync with macOS system clipboard
opt.mouse = "a"

-- Window splitting
opt.splitright = true
opt.splitbelow = true

-- Behavior & Performance
opt.updatetime = 250
opt.timeoutlen = 300
opt.undofile = true -- Persistent undo
opt.scrolloff = 8   -- Minimal lines above/below cursor
opt.sidescrolloff = 8
opt.wrap = false    -- Disable line wrapping by default
opt.completeopt = { "menu", "menuone", "noselect" }
