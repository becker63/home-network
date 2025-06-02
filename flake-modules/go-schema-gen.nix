{ pkgs, lib, src, gomod2nix }:

gomod2nix.buildGoApplication {
  pname = "schema-gen";
  version = "0.1.0";

  src = pkgs.lib.cleanSourceWith {
    src = src;
    filter = path: type: true;
  };

  # You must have a generated gomod2nix.toml next to your go.mod
  # You can generate it via: `nix run .#gomod2nix` (once defined in the flake)
  modules = ./gomod2nix.toml;

  CGO_ENABLED = "0";
  doCheck = false;
}