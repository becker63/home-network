{
  config,
  pkgs,
  lib,
  ...
}:

let
  vip = builtins.getEnv "FRP_VIRTUAL_IP";
in
{
  networking.hostName = lib.mkForce "frp-slave";

  systemd.services.keepalived = {
    enable = true;
    wantedBy = [ "multi-user.target" ];
    serviceConfig.ExecStart = "${pkgs.keepalived}/bin/keepalived -f /etc/keepalived/keepalived.conf";
  };

  environment.etc."keepalived/keepalived.conf".text = ''
    vrrp_instance VI_1 {
      state BACKUP
      interface eth0
      virtual_router_id 51
      priority 100
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
