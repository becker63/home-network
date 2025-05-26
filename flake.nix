{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
        "aarch64-darwin"
      ];

      perSystem =
        { pkgs, ... }:
        let
          shell = with pkgs; [
            zoxide
            fd
            eza
            just
            zsh
            git
          ];

          nixTools = with pkgs; [
            nixfmt-rfc-style
            nil
            nixd
          ];

          kubeTools = with pkgs; [
            talosctl
            kind
            kubectl
            kuttl
            kubernetes-helm
	          kcl
          ];

          nimTools = with pkgs; [
            nim
            nimble
          ];

          allTools = shell ++ nixTools ++ kubeTools ++ nimTools;

          kindShellHook = ''
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
          '';
        in
        {
          devShells.default = pkgs.mkShell {
            packages = allTools;

            shellHook = ''
              ${kindShellHook}
              echo "🐥 Nim + Nix + Kubernetes dev shell ready"

              if [ -n "$PS1" ] && [ -z "$IN_NIX_DEV_ZSH" ] && [ -z "$ZSH_VERSION" ]; then
                export IN_NIX_DEV_ZSH=1
                exec zsh
              fi
            '';
          };
        };
    };
}
