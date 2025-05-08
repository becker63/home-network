{
  description = "Dev shell with nixd and qcow2 image support";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
    nixos-generators.url = "github:nix-community/nixos-generators";
  };

  outputs = { self, nixpkgs, flake-utils, nixos-generators, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };

        # Define the QCOW2 image package
        qcowImagePkg = nixos-generators.nixosGenerate {
          system = "x86_64-linux"; # Build platform
          format = "qcow";
          modules = [
            {
              nixpkgs.buildPlatform = "x86_64-linux";
              nixpkgs.hostPlatform = "aarch64-linux"; # Target platform
            }
            ./phases/one_bootstrap/nix_configs/cloud_frp/configuration.nix
          ];
        };
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            # Editor tools
            nixfmt-rfc-style
            nil
            nixd
            direnv

            # Needed pkgs
            terraform
            just
            pre-commit
            talosctl

            # Python
            python313
            uv
          ];
          shellHook = ''
            if [ -z "$IN_NIX_SHELL_ZSH" ]; then
              export IN_NIX_SHELL_ZSH=1
              exec zsh
            fi
          '';
        };

        packages = {
          qcowImage = qcowImagePkg;
        };
      });
}
