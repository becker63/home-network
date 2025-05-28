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

          # Import python cli/pkg creator
          makePythonCli = import ./flake-modules/make-python-cli.nix;

          # Our custom python based shell script!

          pyCliTools = [
            # TODO: maybe automate this by globbing cli dir
            (makePythonCli {
              inherit pkgs;
              name = "jsontotoml";
              scriptPath = ./scripts/src/cli/JsontoToml.py;
              python = pythonEnv.virtualenv;
            })
            (makePythonCli {
              inherit pkgs;
              name = "manual_iter_test";
              scriptPath = ./scripts/src/cli/manual_iter_test.py;
              python = pythonEnv.virtualenv;
            })
          ];

          nixTools = with pkgs; [
            nixfmt-rfc-style
            nil
            nixd
          ];

          shellTools = with pkgs; [
            zoxide
            fd
            eza
            just
            zsh
            git
            uv
          ];

          kubeTools = with pkgs; [
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
            packages = nixTools ++ shellTools ++ [ pythonEnv.virtualenv ] ++ kubeTools ++ pyCliTools;

            env = {
              # UV_NO_SYNC = "1";
              UV_PYTHON = "${pythonEnv.virtualenv}/bin/python";
              UV_PYTHON_DOWNLOADS = "never";
            };

            shellHook = ''
              unset PYTHONPATH
              export REPO_ROOT=$(git rev-parse --show-toplevel)
              export PYTHONPATH=$PWD/scripts/src:$PYTHONPATH

              # Run the kind shell hook script
              ${kindShellScript}/bin/kind-shell-hook

              echo "🐍 Python dev shell (uv2nix) ready 🐥"

              # Only exec zsh if current shell is NOT zsh
                if [ -n "$PS1" ] && [ -z "$ZSH_VERSION" ]; then
                  exec zsh
                fi
            '';
          };
        };
    };
}
