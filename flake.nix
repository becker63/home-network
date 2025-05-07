{
  description = "Dev shell with nixd";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        inherit (pkgs) mkShell nixd;
      in {
        devShells.default = mkShell {
          packages = [
            nixd
            python313
            terraform_1_11
            just
            direnv
            talosctl
            pre-commit
            uv
          ];

          shellHook = ''
              if [ -z "$IN_NIX_SHELL_ZSH" ]; then
                export IN_NIX_SHELL_ZSH=1
                exec zsh
              fi
            '';
        };
      }
    );
}
