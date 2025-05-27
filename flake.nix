{
  description = "Nim + Kubernetes + uv2nix Python dev environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    uv2nix.url = "github:pyproject-nix/uv2nix";
    pyproject-nix.url = "github:pyproject-nix/pyproject.nix";
    pyproject-build-systems.url = "github:pyproject-nix/build-system-pkgs";

    # Make dependencies follow nixpkgs
    uv2nix.inputs.nixpkgs.follows = "nixpkgs";
    uv2nix.inputs.pyproject-nix.follows = "pyproject-nix";
    pyproject-nix.inputs.nixpkgs.follows = "nixpkgs";
    pyproject-build-systems.inputs.nixpkgs.follows = "nixpkgs";
    pyproject-build-systems.inputs.pyproject-nix.follows = "pyproject-nix";
    pyproject-build-systems.inputs.uv2nix.follows = "uv2nix";
  };

  outputs =
    inputs@{
      self,
      nixpkgs,
      flake-parts,
      uv2nix,
      pyproject-nix,
      pyproject-build-systems,
      ...
    }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
        "aarch64-darwin"
      ];

      perSystem =
        { pkgs, system, ... }:
        let
          uv2nixLib = uv2nix.lib;

          # Import Python environment module
          pythonEnv = import ./flake-modules/python.nix {
            inherit
              pkgs
              system
              uv2nixLib
              pyproject-nix
              pyproject-build-systems
              ;

            workspaceRoot = ./scripts;
          };

          # Import kind shell hook script generator
          kindShellScript = import ./flake-modules/kind-init.nix { inherit pkgs; };

          shellTools = with pkgs; [
            zoxide
            fd
            eza
            just
            zsh
            git
            uv
            nixfmt-rfc-style
            nil
            nixd
            talosctl
            kind
            kubectl
            kuttl
            kubernetes-helm
            kcl
            go
            
          ];

        in
        {
          devShells.default = pkgs.mkShell {
            packages = shellTools ++ [ pythonEnv.virtualenv ];

            env = {
              UV_NO_SYNC = "1";
              UV_PYTHON = "${pythonEnv.virtualenv}/bin/python";
              UV_PYTHON_DOWNLOADS = "never";
            };

            shellHook = ''
              unset PYTHONPATH
              export REPO_ROOT=$(git rev-parse --show-toplevel)

              # Run the kind shell hook script
              ${kindShellScript}/bin/kind-shell-hook

              echo "🐍 Python dev shell (uv2nix) ready 🐥"

              if [ -n "$PS1" ] && [ -z "$IN_NIX_DEV_ZSH" ] && [ -z "$ZSH_VERSION" ]; then
                export IN_NIX_DEV_ZSH=1
                exec zsh
              fi
            '';
          };
        };
    };
}
