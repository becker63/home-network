{
  description = "Dev shell + QCOW2 image builder (x86-only)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
    nixos-generators.url = "github:nix-community/nixos-generators";
    go119pkgs = {
      url = "github:NixOS/nixpkgs/5a83f6f984f387d47373f6f0c43b97a64e7755c0";
      flake = false;
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      nixos-generators,
      go119pkgs,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };

        legacyPkgs = import go119pkgs { inherit system; };

        buildOnX86_64Linux = [
          (
            { ... }:
            {
              nixpkgs.hostPlatform = "x86_64-linux";
              nixpkgs.buildPlatform = "x86_64-linux";
            }
          )
        ];

        # 💡 Shared tools between dev shells
        commonShellTools = with pkgs; [
          zoxide
          fd
          eza
          direnv
          git-crypt
          curl
          unzip
          just
          bun
        ];

      in
      {
        devShells = {
          # 🧪 Main Dev Shell
          default = pkgs.mkShell {
            packages =
              with pkgs;
              commonShellTools
              ++ [
                nixfmt-rfc-style
                nil
                nixd
                bun
                talosctl
                kind
                kubectl
                kuttl
                just
                nodejs
                go
                gopls
                kubernetes-helm
              ];

            shellHook = ''
              if [ -f ./secrets/git-crypt.key ]; then
                git-crypt unlock ./secrets/git-crypt.key 2>/dev/null || true
              fi

              if ! kind get clusters | grep -q "^kuttl$"; then
                echo "🔧 Spinning up Kind cluster 'kuttl'..."
                kind create cluster --name kuttl
              else
                echo "✅ Kind cluster 'kuttl' already exists"
              fi

              kind get kubeconfig --name kuttl > ./kubeconfig
              export KUBECONFIG="$PWD/kubeconfig"

              echo "🌱 KUBECONFIG: $KUBECONFIG"
              echo "👉 Current context: $(kubectl config current-context)"
              echo "Bun installing for you"
              bun install

              if [ -z "$IN_NIX_SHELL_ZSH" ]; then
                export IN_NIX_SHELL_ZSH=1
                exec zsh
              fi
            '';
          };

          # ⚙️ Upjet Provider Dev Shell
          upjet-env = pkgs.mkShell {
            packages = commonShellTools ++ [
              legacyPkgs.go_1_19
              pkgs.terraform
              pkgs.gnumake
              pkgs.pkg-config
              pkgs.git
            ];

            shellHook = ''
              echo "🧪 Upjet Dev Shell Loaded"
              echo "Using Go version: $(go version)"
              export GOCACHE=$PWD/.cache/go-build

              if [ -z "$IN_NIX_SHELL_ZSH" ]; then
                export IN_NIX_SHELL_ZSH=1
                exec zsh
              fi
            '';
          };
        };
      }
    );
}
