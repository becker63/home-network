{ pkgs }:

pkgs.writeShellScriptBin "kind-shell-hook" ''
  #!/usr/bin/env bash
  if ! kind get clusters | grep -q "^kuttl$"; then
    echo "🔧 Spinning up Kind cluster 'kuttl'..."
    kind create cluster --name kuttl
  else
    echo "✅ Kind cluster 'kuttl' already exists"
  fi

  kind get kubeconfig --name kuttl > ./kubeconfig
  export KUBECONFIG="$PWD/kubeconfig"
  echo "🌱 KUBECONFIG: $KUBECONFIG"
  echo "👉 Current context: $(kubectl config current-context)"
''
