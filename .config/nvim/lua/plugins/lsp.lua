return {
  {
    "neovim/nvim-lspconfig",
    dependencies = {
      "williamboman/mason.nvim",
      "williamboman/mason-lspconfig.nvim",
      "j-hui/fidget.nvim",
    },
    config = function()
      require("fidget").setup({})
      require("mason").setup({
        ui = {
          border = "rounded",
          icons = {
            package_installed = "✓",
            package_pending = "➜",
            package_uninstalled = "✗",
          },
        },
      })

      local capabilities = vim.lsp.protocol.make_client_capabilities()
      local cmp_ok, cmp_nvim_lsp = pcall(require, "cmp_nvim_lsp")
      if cmp_ok then
        capabilities = cmp_nvim_lsp.default_capabilities(capabilities)
      end

      -- Attach LSP keymaps on buffer attach
      vim.api.nvim_create_autocmd("LspAttach", {
        group = vim.api.nvim_create_augroup("UserLspConfig", {}),
        callback = function(ev)
          local nmap = function(keys, func, desc)
            if desc then
              desc = "LSP: " .. desc
            end
            vim.keymap.set("n", keys, func, { buffer = ev.buf, desc = desc })
          end

          nmap("gd", vim.lsp.buf.definition, "Goto Definition")
          nmap("gD", vim.lsp.buf.declaration, "Goto Declaration")
          nmap("gr", vim.lsp.buf.references, "Goto References")
          nmap("gI", vim.lsp.buf.implementation, "Goto Implementation")
          nmap("<leader>D", vim.lsp.buf.type_definition, "Type Definition")
          nmap("K", vim.lsp.buf.hover, "Hover Documentation")
          nmap("<leader>rn", vim.lsp.buf.rename, "Rename Symbol")
          nmap("<leader>ca", vim.lsp.buf.code_action, "Code Action")
          nmap("<leader>f", function()
            vim.lsp.buf.format({ async = true })
          end, "Format Document")
        end,
      })

      -- Modern Neovim 0.11+ / 0.12+ native LSP configuration
      vim.lsp.config("*", {
        capabilities = capabilities,
      })

      vim.lsp.config("lua_ls", {
        settings = {
          Lua = {
            diagnostics = {
              globals = { "vim" },
            },
            workspace = {
              library = vim.api.nvim_get_runtime_file("", true),
              checkThirdParty = false,
            },
            telemetry = { enable = false },
          },
        },
      })

      require("mason-lspconfig").setup({
        ensure_installed = {
          "lua_ls",
          "ts_ls",
          "pyright",
          "jsonls",
          "yamlls",
        },
        automatic_enable = true,
      })

      -- Native nix LSP setup if nixd or nil is installed via nix
      if vim.fn.executable("nixd") == 1 then
        vim.lsp.enable("nixd")
      elseif vim.fn.executable("nil") == 1 then
        vim.lsp.enable("nil_ls")
      end
    end,
  },
}
