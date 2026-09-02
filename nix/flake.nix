{
  description = "DarkRader nix-darwin system flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    nix-darwin.url = "github:nix-darwin/nix-darwin/master";
    nix-darwin.inputs.nixpkgs.follows = "nixpkgs";
    nix-homebrew.url = "github:zhaofengli/nix-homebrew";
  };

  outputs = { self, nix-darwin, nix-homebrew, ... }:
  let
    commonModules = user: [
      ./shared.nix
      nix-homebrew.darwinModules.nix-homebrew
      {
        system.configurationRevision = self.rev or self.dirtyRev or null;
        system.primaryUser = user;

        nix-homebrew = {
          enable = true;
          enableRosetta = true;
          user = user;
          autoMigrate = true;

          trust.taps = [
            "hashicorp/tap"
          ];
        };
      }
    ];

    mkMacbook = { profile, user }: nix-darwin.lib.darwinSystem {
      modules = commonModules user ++ [ profile ];
    };
  in
  {
    darwinConfigurations."macbook-personal" =
      mkMacbook {
        profile = ./personal;
        user = "Artyom";
      };

    darwinConfigurations."macbook-work" =
      mkMacbook {
        profile = ./work;
        user = "artem";
      };

    darwinPackages =
      self.darwinConfigurations."macbook-personal".pkgs;
  };
}
