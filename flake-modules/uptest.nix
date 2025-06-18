{ pkgs }:

let
  uptestSrc = pkgs.fetchFromGitHub {
    owner = "crossplane";
    repo = "uptest";
    rev = "188d1abb7d4c042b00a1232ad056f6356a398108";
    hash = "sha256-lbZP31CrQbK4OQMHtg7KaP5UADbuOlTm6r2g4jA+qQQ=";
  };
in {
  uptest = pkgs.buildGoModule {
    pname = "uptest";
    version = "0.1.0";

    src = uptestSrc;
    vendorHash = "sha256-FB9umtWc3DzEbxK3ZYq7QM5sCG4HLg7PwEgCr7nOPCo=";

    subPackages = [ "cmd/uptest" ];

    installPhase = ''
      mkdir -p $out/bin
      cp $GOPATH/bin/uptest $out/bin/
    '';
  };
}