{
  description = "Dev shell + QCOW2 image builder (x86-only)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
    nixos-generators.url = "github:nix-community/nixos-generators";
  };

  outputs =
    {
      nixpkgs,
      flake-utils,
      nixos-generators,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };

        buildOnX86_64Linux = [
          (
            { ... }:
            {
              nixpkgs.hostPlatform = "x86_64-linux";
              nixpkgs.buildPlatform = "x86_64-linux";
            }
          )
        ];

        qcowPackages = import ./flake_modules/frp_qcow.nix {
          inherit
            pkgs
            system
            nixos-generators
            buildOnX86_64Linux
            ;
        };
      in
      {
        # Developer shell (works on all systems)
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            # Editor tools
            nixfmt-rfc-style
            nil
            nixd
            direnv

            # Needed pkgs
            bun
            talosctl
            git-crypt
            kind # Add kind for local k8s
            kubectl # Needed to interact with kind
            kuttl # KUTTL CLI (if available; otherwise, install manually)
            just
            nodejs

            # Things I like
            zoxide
            fd
            eza
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

            export KUBECONFIG="$(kind get kubeconfig-path --name kuttl 2>/dev/null || echo $HOME/.kube/config)"
            kubectl config use-context kind-kuttl

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

        packages = qcowPackages;
      }
    );
}
