from sopsy import Sops
from invoke.tasks import task
import json
import os
from pathlib import Path
from root_config import PHASES_DIR, KUBECONFIG_DIR

SOPS_AGE_KEY_FILE = Path.home() / ".config/sops/age/keys.txt"
TFVARS_GLOB = "terraform.auto.tfvars.json"
KUBECONFIG_GLOB = "*.yaml"

os.environ["SOPS_AGE_KEY_FILE"] = str(SOPS_AGE_KEY_FILE)

def is_sops_encrypted(content: str) -> bool:
    return (
        "sops:" in content or
        '"sops"' in content or
        content.strip().startswith("ENC[")
    )

def get_secret_files():
    tfvar_files = list(PHASES_DIR.rglob(TFVARS_GLOB))
    kubeconfig_files = list(KUBECONFIG_DIR.rglob(KUBECONFIG_GLOB))
    return tfvar_files + kubeconfig_files

@task
def encrypt_all(c):
    """
    Encrypt all terraform.auto.tfvars.json and kubeconfig YAML files if not already encrypted.
    """
    all_files = get_secret_files()
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
    Decrypt all terraform.auto.tfvars.json and kubeconfig YAML files and write as plaintext JSON/YAML.
    """
    all_files = get_secret_files()

    if not all_files:
        print("⚠️  No files to decrypt.")
        return

    for file_path in all_files:
        print(f"🔓 Decrypting and writing: {file_path}")
        sops = Sops(file_path)
        decrypted = sops.decrypt()

        if isinstance(decrypted, dict):
            content = json.dumps(decrypted, indent=2)
        elif isinstance(decrypted, bytes):
            content = decrypted.decode()
        elif isinstance(decrypted, str):
            content = decrypted
        else:
            raise TypeError(f"Unexpected decrypt output type: {type(decrypted)}")

        file_path.write_text(content)
