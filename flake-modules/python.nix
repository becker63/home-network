{
  pkgs,
  system,
  uv2nixLib,
  pyproject-nix,
  pyproject-build-systems,
  workspaceRoot,
}:

let
  workspace = uv2nixLib.workspace.loadWorkspace {
    inherit workspaceRoot;
  };

  overlay = workspace.mkPyprojectOverlay {
    sourcePreference = "wheel";
  };

  editableOverlay = workspace.mkEditablePyprojectOverlay {
    root = "$REPO_ROOT"; # runtime env var
  };

  python = pkgs.python313;

  pythonSet =
    (pkgs.callPackage pyproject-nix.build.packages {
      inherit python;
    }).overrideScope
      (
        pkgs.lib.composeManyExtensions [
          pyproject-build-systems.overlays.default
          overlay
          editableOverlay
        ]
      );

  virtualenv = pythonSet.mkVirtualEnv "scripts-dev-env" workspace.deps.all;

in
{
  inherit virtualenv;
}
