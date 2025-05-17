{
  description = "Dev shell + QCOW2 image builder (x86-only)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
    nixos-generators.url = "github:nix-community/nixos-generators";
  };

  outputs =
    {
      self,
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

        isX86_64Linux = system == "x86_64-linux";

        baseModules = [
          (
            { ... }:
            {
              nixpkgs.hostPlatform = "x86_64-linux";
              nixpkgs.buildPlatform = "x86_64-linux";
            }
          )
        ];
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
            conftest

            # Things I like
            zoxide
            fd
            eza
          ];

          shellHook = ''
            if [ -f ./secrets/git-crypt.key ]; then
              git-crypt unlock ./secrets/git-crypt.key 2>/dev/null || true
            fi

            if [ -z "$IN_NIX_SHELL_ZSH" ]; then
              export IN_NIX_SHELL_ZSH=1
              exec zsh
            fi
          '';
        };

        # Only expose qcow2 image build outputs for x86_64-linux
        packages =
          if isX86_64Linux then
            {
              master-qcow = nixos-generators.nixosGenerate {
                inherit system;
                format = "qcow";
                modules = baseModules ++ [
                  ./phases/0_bootstrap/frp_nix_config/configuration.nix
                  ./phases/0_bootstrap/frp_nix_config/master.nix
                ];
              };

              slave-qcow = nixos-generators.nixosGenerate {
                inherit system;
                format = "qcow";
                modules = baseModules ++ [
                  ./phases/0_bootstrap/frp_nix_config/configuration.nix
                  ./phases/0_bootstrap/frp_nix_config/slave.nix
                ];
              };
            }
          else
            { };
      }
    );
}
