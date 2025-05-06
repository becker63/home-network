from sopsy import Sops
from invoke.tasks import task
import json
from config import PROJECT_ROOT, TALOS_HOME_MAIN_KUBECONFIG_PATH
import os
from pathlib import Path

os.environ["SOPS_AGE_KEY_FILE"] = str(Path.home() / ".config/sops/age/keys.txt")


def is_sops_encrypted(content: str) -> bool:
    return (
        "sops:" in content or     # YAML
        '"sops"' in content or    # JSON
        content.strip().startswith("ENC[")  # inline format (e.g. .env files)
    )


@task
def encrypt_all(c):
    """
    Encrypt all terraform.auto.tfvars.json files and kubeconfig.yaml if not already encrypted.
    """
    tfvar_files = list((PROJECT_ROOT / "terraform").rglob("terraform.auto.tfvars.json"))
    kubeconfig = TALOS_HOME_MAIN_KUBECONFIG_PATH
    all_files = tfvar_files + ([kubeconfig] if kubeconfig.exists() else [])

    print(f"📁 Encrypting files: {all_files}")

    for file_path in all_files:
        content = file_path.read_text()
        if is_sops_encrypted(content):
            print(f"⏭️  Skipping already encrypted file: {file_path}")
            continue

        print(f"🔐 Encrypting {file_path}")
        sops = Sops(file_path, in_place=True)
        sops.encrypt()


@task
def decrypt_all(c):
    """
    Decrypt all terraform.auto.tfvars.json files and kubeconfig.yaml and overwrite with valid JSON or YAML.
    """
    tfvar_files = list((PROJECT_ROOT / "terraform").rglob("terraform.auto.tfvars.json"))
    kubeconfig = TALOS_HOME_MAIN_KUBECONFIG_PATH
    all_files = tfvar_files + ([kubeconfig] if kubeconfig.exists() else [])

    if not all_files:
        print("⚠️  No files to decrypt.")
        return

    for file_path in all_files:
        print(f"🔓 Decrypting and writing: {file_path}")
        sops = Sops(file_path)
        decrypted = sops.decrypt()

        # Normalize all output to string before writing
        if isinstance(decrypted, dict):
            content = json.dumps(decrypted, indent=2)
        elif isinstance(decrypted, bytes):
            content = decrypted.decode()
        elif isinstance(decrypted, str):
            content = decrypted
        else:
            raise TypeError(f"Unexpected decrypt output type: {type(decrypted)}")

        file_path.write_text(content)
