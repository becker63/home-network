{
  description = "Nim + Kubernetes + uv2nix Python + Go dev environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    uv2nix.url = "github:pyproject-nix/uv2nix";
    pyproject-nix.url = "github:pyproject-nix/pyproject.nix";
    pyproject-build-systems.url = "github:pyproject-nix/build-system-pkgs";
    pre-commit-hooks.url = "github:cachix/git-hooks.nix";

    dagger.url = "github:dagger/nix";
    dagger.inputs.nixpkgs.follows = "nixpkgs";

    # Input linking
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
      pre-commit-hooks,
      dagger,
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
          lib = pkgs.lib;
          kindShellScript = import ./flake-modules/kind-init.nix { inherit pkgs; };

          # Python
          uv2nixLib = uv2nix.lib;
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

          makePythonCli = import ./flake-modules/make-python-cli.nix;

          pyCliTools = [
            (makePythonCli {
              inherit pkgs;
              name = "manual_kcl_find";
              scriptPath = ./scripts/src/cli/manual_kcl_find.py;
              python = pythonEnv.virtualenv;
            })
          ];

          gitHooks = import ./flake-modules/git-hooks.nix { inherit lib; };

          pre-commit = pre-commit-hooks.lib.${system}.run {
            src = ./.;
            hooks = gitHooks.pre-commit.hooks;
          };

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
          daggerTools = [ dagger.packages.${system}.dagger ];
        in
        {
          checks.pre-commit-check = pre-commit;

          devShells.default = pkgs.mkShell {
            packages =
              nixTools
              ++ shellTools
              ++ [ pythonEnv.virtualenv ]
              ++ kubeTools
              ++ daggerTools
              ++ pyCliTools
              ++ pre-commit.enabledPackages;

            env = {
              UV_PYTHON = "${pythonEnv.virtualenv}/bin/python";
              UV_PYTHON_DOWNLOADS = "never";
            };

            shellHook = ''
              ${pre-commit.shellHook}

              unset PYTHONPATH
              export REPO_ROOT=$(git rev-parse --show-toplevel)
              export PYTHONPATH=$PWD/scripts/src:$PYTHONPATH

              ${kindShellScript}/bin/kind-shell-hook

              echo "🐍 Python dev shell (uv2nix) ready 🐥"

              # TODO: fix gomodnix
              cd $REPO_ROOT/kcl/schemas/go
              go mod tidy
              cd -

              if [ -n "$PS1" ] && [ -z "$ZSH_VERSION" ]; then
                exec zsh
              fi
            '';
          };
        };
    };
}
