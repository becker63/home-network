{
  pkgs,
  name,
  scriptPath,
  python,
}:

pkgs.stdenv.mkDerivation {
  pname = name;
  version = "0.1";

  buildInputs = [ python ];

  phases = [ "installPhase" ];

  installPhase = ''
    mkdir -p $out/bin
    cp ${scriptPath} $out/bin/${name}.py
    cat > $out/bin/${name} <<EOF
    #!/bin/sh
    exec ${python}/bin/python $out/bin/${name}.py "\$@"
    EOF
    chmod +x $out/bin/${name}
  '';
}
