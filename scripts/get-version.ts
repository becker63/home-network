// scripts/get-version.ts
import * as fs from "fs";

const [, , key] = process.argv;
if (!key) {
  console.error("❌ Missing key. Usage: bun run get-version.ts KEY");
  process.exit(1);
}

const secrets = JSON.parse(fs.readFileSync("secrets.json", "utf-8"));

if (!(key in secrets)) {
  console.error(`❌ Key not found: ${key}`);
  process.exit(1);
}

console.log(secrets[key]);
