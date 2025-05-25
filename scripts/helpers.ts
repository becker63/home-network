import * as fs from "fs";
import { spawn } from "bun";
import { readFileSync } from "fs";
import { join } from "path";
import { Construct } from "constructs";
import { Secret } from "cdk8s-plus-32";
import * as path from "path";

const secretsPath = join(process.cwd(), "secrets.json");

let secrets: Record<string, string> = {};
try {
  const fileContents = readFileSync(secretsPath, "utf8");
  secrets = JSON.parse(fileContents);
} catch (err) {
  console.warn(`⚠️ Unable to load secrets.json at ${secretsPath}: ${err}`);
}

/**
 * Get a secret value from secrets.json.
 * @param key The key to look up.
 */
export function getSecret(key: string): string {
  const value = secrets[key];
  if (!value) {
    throw new Error(`Secret "${key}" not found in secrets.json`);
  }
  return value;
}

export function assertDirExists(dir: string): void {
  if (!fs.existsSync(dir) || !fs.statSync(dir).isDirectory()) {
    console.error(`❌ Directory does not exist: ${dir}`);
    process.exit(1);
  }
}

export async function runCommand(cmd: string[], cwd: string) {
  const proc = spawn({ cmd, cwd, stdout: "inherit", stderr: "inherit" });
  const exitCode = await proc.exited;
  if (exitCode !== 0) {
    throw new Error(`❌ Command failed: ${cmd.join(" ")}`);
  }
}

export function createSecretsFromFile(scope: Construct): void {
  const secretsPath = path.join(process.cwd(), "secrets.json");

  if (!fs.existsSync(secretsPath)) {
    throw new Error(`❌ Missing secrets.json at ${secretsPath}`);
  }

  let secrets: Record<string, string>;
  try {
    const fileContent = fs.readFileSync(secretsPath, "utf8");
    secrets = JSON.parse(fileContent);
  } catch (err) {
    throw new Error(`❌ Failed to parse secrets.json: ${err}`);
  }

  new Secret(scope, "ProjectSecrets", {
    metadata: {
      name: "project-secrets",
      namespace: "crossplane-system",
    },
    stringData: secrets,
  });
}
