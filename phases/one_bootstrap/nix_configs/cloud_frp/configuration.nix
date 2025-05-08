{ pkgs, lib, ... }:

let
  hostname = builtins.getEnv "FRP_HOSTNAME";
  isMaster = lib.strings.hasInfix "1" hostname; # e.g., frp-node-1 is master
in
{
  networking.hostName = lib.mkDefault hostname;

}
