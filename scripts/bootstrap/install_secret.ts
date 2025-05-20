import * as fs from "fs";
import * as path from "path";
import * as yaml from "js-yaml";

const secretName = "my-secret";
const namespace = "default";
const inputPath = path.resolve("config/secrets.json");
const outputPath = path.resolve(`secrets/sealed-${secretName}.yaml`);
const certPath = path.resolve("sealed-secrets-public.pem"); // ← Make sure this exists

// Step 1: Load your JSON secrets
const secrets = JSON.parse(fs.readFileSync(inputPath, "utf-8"));

// Step 2: Build the Kubernetes Secret object
const plainSecret = {
  apiVersion: "v1",
  kind: "Secret",
  metadata: { name: secretName, namespace },
  type: "Opaque",
  data: Object.fromEntries(
    Object.entries(secrets).map(([key, val]) => [
      key,
      Buffer.from(val as string).toString("base64"),
    ]),
  ),
};

const tmpSecretPath = path.resolve(".tmp-secret.yaml");
fs.writeFileSync(tmpSecretPath, yaml.dump(plainSecret));
console.log(`✅ Wrote temp secret manifest to ${tmpSecretPath}`);

// Step 3: Seal the secret using `kubeseal` via Bun.spawn
console.log("🔐 Running kubeseal...");
const seal = Bun.spawn({
  cmd: [
    "kubeseal",
    "--format",
    "yaml",
    "--cert",
    certPath,
    "--namespace",
    namespace,
    "--name",
    secretName,
    "-o",
    "yaml",
    "-f",
    tmpSecretPath,
  ],
  stdout: "pipe",
  stderr: "inherit",
});

const sealed = await new Response(seal.stdout).text();
if (seal.exitCode !== 0) {
  console.error("❌ kubeseal failed");
  process.exit(1);
}

// Step 4: Save the sealed output
fs.mkdirSync("secrets", { recursive: true });
fs.writeFileSync(outputPath, sealed);
console.log(`✅ SealedSecret written to ${outputPath}`);

// Cleanup
fs.unlinkSync(tmpSecretPath);
