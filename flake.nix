{
  description = "Dev shell + QCOW2 image builder (x86-only)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
    nixos-generators.url = "github:nix-community/nixos-generators";
    pre-commit-hooks-nix.url = "github:cachix/pre-commit-hooks.nix";
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
      pre-commit-hooks-nix,
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

        commonShellTools = with pkgs; [
          zoxide
          fd
          eza
          direnv
          curl
          unzip
          just
          bun
          sops
          age
        ];

        sharedShellHook = ''
          echo "💡 Running shared dev shell hook"

          if [ -f ./secrets.json ]; then
            echo "🔓 Attempting to decrypt secrets.json in place..."
            ./scripts/sops/sops-decrypt.sh secrets.json
          fi

          echo "📦 Running \`bun install\`..."
          bun install

          if [ -n "$PS1" ] && [ -z "$ZSH_VERSION" ]; then
            exec zsh
          fi
        '';

        # Pre-commit hook setup
        pre-commit = pre-commit-hooks-nix.lib.${system}.run {
          src = ./.;
          hooks = {
            sops-encrypt = {
              enable = true;
              entry = "./scripts/sops/sops-encrypt.sh";
              files = "^secrets\\.json$";
              language = "system";
              pass_filenames = true;
            };
          };
        };

        terraform_1_3_3 = pkgs.stdenv.mkDerivation {
          name = "terraform-1.3.3";
          src = pkgs.fetchzip {
            url = "https://releases.hashicorp.com/terraform/1.3.3/terraform_1.3.3_darwin_arm64.zip";
            sha256 = "04244xbxmj9hmmvm0bvy0dg350grb415zy8y04zx00a1bfzsqwaw";
          };
          phases = [ "installPhase" ];
          installPhase = ''
            mkdir -p $out/bin
            cp $src/terraform $out/bin/
          '';
        };

      in
      {
        devShells = {
          default = pkgs.mkShell {
            packages =
              with pkgs;
              commonShellTools
              ++ [
                nixfmt-rfc-style
                nil
                nixd
                talosctl
                kind
                kubectl
                kuttl
                nodejs
                go
                gopls
                kubernetes-helm
              ];

            shellHook = ''
              ${pre-commit.shellHook}
              ${sharedShellHook}

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

              echo "📜 Applying CRDs from ./crds..."
              kubectl apply -f ./crds
            '';
          };

          upjet-env = pkgs.mkShell {
            packages = commonShellTools ++ [
              legacyPkgs.go_1_19
              pkgs.gnumake
              pkgs.pkg-config
              pkgs.git
              terraform_1_3_3
            ];

            shellHook = ''
              export IN_DEV_UPJET=1
              ${sharedShellHook}
              echo "🧪 Upjet Dev Shell Loaded"
              echo "Using Go version: $(go version)"
              export GOCACHE=$PWD/.cache/go-build
            '';
          };
        };
      }
    );
}
