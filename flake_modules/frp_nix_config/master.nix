{ pkgs, lib, ... }:

let
  vip = builtins.getEnv "FRP_VIRTUAL_IP";
in
{
  networking.hostName = lib.mkForce "frp-master";

  systemd.services.keepalived = {
    enable = true;
    wantedBy = [ "multi-user.target" ];
    serviceConfig.ExecStart = "${pkgs.keepalived}/bin/keepalived -f /etc/keepalived/keepalived.conf";
  };

  environment.etc."keepalived/keepalived.conf".text = ''
    vrrp_instance VI_1 {
      state MASTER
      interface eth0
      virtual_router_id 51
      priority 101
      advert_int 1
      authentication {
        auth_type PASS
        auth_pass secret
      }
      virtual_ipaddress {
        ${vip}
      }
    }
  '';
}
