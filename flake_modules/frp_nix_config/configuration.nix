{ pkgs, lib, ... }:

{
  networking.hostName = lib.mkDefault "frp-node";
  services.openssh.enable = true;

  users.users.root.openssh.authorizedKeys.keys = [ "ssh-ed25519 AAAAC3Nz... yourkey" ];

  environment.systemPackages = with pkgs; [
    frp
    keepalived
  ];

  system.stateVersion = "24.05";
}
