{
  description = "DarkRader nix-darwin system flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    nix-darwin.url = "github:nix-darwin/nix-darwin/master";
    nix-darwin.inputs.nixpkgs.follows = "nixpkgs";
    nix-homebrew.url = "github:zhaofengli/nix-homebrew";
    darwin-custom-icons.url = "github:ryanccn/nix-darwin-custom-icons";
  };

  outputs = { self, nix-darwin, nix-homebrew, darwin-custom-icons, ... }:
  let
    commonModules = { user, home ? "/Users/${user}" }: [
      ./shared.nix
      nix-homebrew.darwinModules.nix-homebrew
      darwin-custom-icons.darwinModules.default
      {
        system.configurationRevision = self.rev or self.dirtyRev or null;
        system.primaryUser = user;

        _module.args = {
          inherit user;
          userHome = home;
        };

        nix-homebrew = {
          enable = true;
          enableRosetta = true;
          user = user;
          autoMigrate = true;

          trust.taps = [
            "hashicorp/tap"
            "DarkRader/tap"
          ];
        };
      }
    ];

    mkMacbook = { profile, user, home ? "/Users/${user}" }: nix-darwin.lib.darwinSystem {
      modules = commonModules { inherit user home; } ++ [ profile ];
    };
  in
  {
    darwinConfigurations."macbook-personal" =
      mkMacbook {
        profile = ./personal;
        user = "Artyom";
        home = "/Users/Artyom_1";
      };

    darwinConfigurations."macbook-work" =
      mkMacbook {
        profile = ./work;
        user = "artem";
        home = "/Users/artem";
      };

    darwinPackages =
      self.darwinConfigurations."macbook-personal".pkgs;
  };
}
