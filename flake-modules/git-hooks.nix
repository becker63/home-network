{ lib, ... }:
{
  pre-commit = {
    hooks = {
      deny-plaintext-secrets = {
        enable = true;
        entry = ''
          bash -c '
          if grep -r --exclude-dir=.git "api_key:" secrets/plaintext 2>/dev/null; then
            echo "❌ Refusing commit: plaintext secrets detected in secrets/plaintext/"
            exit 1
          fi
          echo "✅ No plaintext secrets found."
          '
        '';
        files = "secrets/plaintext/";
        pass_filenames = false;
      };
    };
  };
}
