{
  system,
  nixos-generators,
  buildOnX86_64Linux,
  ...
}:

let
  isX86_64Linux = system == "x86_64-linux";
in
if isX86_64Linux then
  {
    master-qcow = nixos-generators.nixosGenerate {
      inherit system;
      format = "qcow";
      modules = buildOnX86_64Linux ++ [
        ./frp_nix_config/configuration.nix
        ./frp_nix_config/master.nix
      ];
    };

    slave-qcow = nixos-generators.nixosGenerate {
      inherit system;
      format = "qcow";
      modules = buildOnX86_64Linux ++ [
        ./frp_nix_config/configuration.nix
        ./frp_nix_config/slave.nix
      ];
    };
  }
else
  { }
