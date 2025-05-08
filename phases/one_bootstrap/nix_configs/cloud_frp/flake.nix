{
  description = "QCOW2 images for FRP master and slave nodes";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    nixos-generators.url = "github:nix-community/nixos-generators";
  };

  outputs =
    {
      self,
      nixpkgs,
      nixos-generators,
      ...
    }:
    let
      system = "x86_64-linux";

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
      packages.${system} = {
        master-qcow = nixos-generators.nixosGenerate {
          inherit system;
          format = "qcow";
          modules = baseModules ++ [
            ./configuration.nix
            ./master.nix
          ];
        };

        slave-qcow = nixos-generators.nixosGenerate {
          inherit system;
          format = "qcow";
          modules = baseModules ++ [
            ./configuration.nix
            ./slave.nix
          ];
        };
      };
    };
}
