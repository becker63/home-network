from sopsy import Sops
from invoke.tasks import task
import json
from config import PROJECT_ROOT
import os
from pathlib import Path

os.environ["SOPS_AGE_KEY_FILE"] = str(Path.home() / ".config/sops/age/keys.txt")

@task
def encrypt_all(c):
    """
    Encrypt all terraform.auto.tfvars.json files under terraform/**/
    if they are not already encrypted.
    """
    base = PROJECT_ROOT / "terraform"
    print(f"📁 Searching in: {base.resolve()}")
    tfvar_files = list(base.rglob("terraform.auto.tfvars.json"))
    print(f"📄 All found tfvars files: {tfvar_files}")

    if not tfvar_files:
        print("⚠️  No tfvars files found to encrypt.")
        return

    for file_path in tfvar_files:
        content = file_path.read_text()
        if '"sops"' in content or content.strip().startswith('{') and '"sops":' in content:
            print(f"⏭️  Skipping already encrypted file: {file_path}")
            continue

        print(f"🔐 Encrypting {file_path}")
        sops = Sops(file_path, in_place=True)
        sops.encrypt()


@task
def decrypt_all(c):
    """
    Decrypt all terraform.auto.tfvars.json files and overwrite with valid JSON.
    """
    base = PROJECT_ROOT / "terraform"
    tfvars_files = list(base.rglob("terraform.auto.tfvars.json"))

    if not tfvars_files:
        print("⚠️  No tfvars files found.")
        return

    for file_path in tfvars_files:
        print(f"🔓 Decrypting and writing: {file_path}")
        sops = Sops(file_path)
        decrypted = sops.decrypt()

        # Normalize all output to a JSON-compatible dict
        if isinstance(decrypted, str):
            data = json.loads(decrypted)
        elif isinstance(decrypted, bytes):
            data = json.loads(decrypted.decode())
        elif isinstance(decrypted, dict):
            data = decrypted
        else:
            raise TypeError(f"Unexpected decrypt output type: {type(decrypted)}")

        # Overwrite with formatted JSON
        file_path.write_text(json.dumps(data, indent=2))
