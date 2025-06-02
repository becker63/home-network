{
  description = "Nim + Kubernetes + uv2nix Python + Go dev environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    uv2nix.url = "github:pyproject-nix/uv2nix";
    pyproject-nix.url = "github:pyproject-nix/pyproject.nix";
    pyproject-build-systems.url = "github:pyproject-nix/build-system-pkgs";
    pre-commit-hooks.url = "github:cachix/git-hooks.nix";

    # go and its closed world assumption 
    # this fork of mine should fix some of the problems with gomod2nix.. thats based on a highly specific commit of its own
    # https://fasterthanli.me/articles/lies-we-tell-ourselves-to-keep-using-golang
    gomod2nix = {
      url = "github:becker63/gomod2nix/159a94a45a694dd1a559ddeb145106ff246e8912";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    # Input linking
    uv2nix.inputs.nixpkgs.follows = "nixpkgs";
    uv2nix.inputs.pyproject-nix.follows = "pyproject-nix";
    pyproject-nix.inputs.nixpkgs.follows = "nixpkgs";
    pyproject-build-systems.inputs.nixpkgs.follows = "nixpkgs";
    pyproject-build-systems.inputs.pyproject-nix.follows = "pyproject-nix";
    pyproject-build-systems.inputs.uv2nix.follows = "uv2nix";
  };

  outputs = inputs@{
    self,
    nixpkgs,
    flake-parts,
    uv2nix,
    pyproject-nix,
    pyproject-build-systems,
    pre-commit-hooks,
    gomod2nix,
    ...
  }: flake-parts.lib.mkFlake { inherit inputs; } {
    systems = [ "x86_64-linux" "aarch64-darwin" ];

    perSystem = { pkgs, system, ... }:
      let
        lib = pkgs.lib;
        kindShellScript = import ./flake-modules/kind-init.nix { inherit pkgs; };

        gomod2nixPkg = gomod2nix.packages.${system}.default;

        # Go module build
        go-modules = gomod2nix.lib.${system}.buildGoApplication {
          pname = "schemas";
          version = "0.1.0";
          src = ./.;
          modules = ./gomod2nix.toml;
        };

        # Python
        uv2nixLib = uv2nix.lib;
        pythonEnv = import ./flake-modules/python.nix {
          inherit pkgs system uv2nixLib pyproject-nix pyproject-build-systems;
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

        nixTools = with pkgs; [ nixfmt-rfc-style nil nixd ];
        shellTools = with pkgs; [ zoxide fd eza just zsh git uv ];
        kubeTools = with pkgs; [
          talosctl kind kubectl kuttl
          kubernetes-helm kcl go
        ];
      in {
        checks.pre-commit-check = pre-commit;

        packages.default = go-modules;

        devShells.default = pkgs.mkShell {
          packages =
            nixTools
            ++ shellTools
            ++ [ pythonEnv.virtualenv ]
            ++ kubeTools
            ++ pyCliTools
            ++ pre-commit.enabledPackages
            ++ [ gomod2nixPkg ];

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
            echo "🧃 gomod2nix available: try \`CGO_ENABLED=0 gomod2nix generate\`"

            if [ -n "$PS1" ] && [ -z "$ZSH_VERSION" ]; then
              exec zsh
            fi
          '';
        };
      };
  };
}