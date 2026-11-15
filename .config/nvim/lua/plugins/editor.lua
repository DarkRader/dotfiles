return {
  -- Show dotfiles by default in Snacks explorer & file picker
  {
    "folke/snacks.nvim",
    opts = {
      picker = {
        sources = {
          explorer = {
            hidden = true, -- Show hidden/dotfiles in the explorer
            ignored = false,
          },
          files = {
            hidden = true, -- Show hidden/dotfiles in find files (<leader>ff, <leader><space>)
          },
        },
      },
    },
  },
}
