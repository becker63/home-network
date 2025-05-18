{
  pkgs,
  system,
  nixos-generators,
  baseModules,
}:

let
  isX86_64Linux = system == "x86_64-linux";
in
if isX86_64Linux then
  {
    master-qcow = nixos-generators.nixosGenerate {
      inherit system;
      format = "qcow";
      modules = baseModules ++ [
        ./frp_nix_config/configuration.nix
        ./frp_nix_config/master.nix
      ];
    };

    slave-qcow = nixos-generators.nixosGenerate {
      inherit system;
      format = "qcow";
      modules = baseModules ++ [
        ./frp_nix_config/configuration.nix
        ./frp_nix_config/slave.nix
      ];
    };
  }
else
  { }
