import * as fs from "fs";
import * as path from "path";
import { spawn } from "bun";

const crdDir = path.resolve("crds");

if (!fs.existsSync(crdDir)) {
  console.error("❌ crds/ directory does not exist.");
  process.exit(1);
}

const files = fs.readdirSync(crdDir).filter((f) => f.endsWith(".yaml"));

if (files.length === 0) {
  console.warn("⚠️ No CRDs found in crds/");
  process.exit(0);
}

console.log(`📥 Importing ${files.length} CRDs into CDK8s...`);

for (const file of files) {
  const fullPath = path.join(crdDir, file);
  console.log(`🔗 Importing ${file}...`);
  const proc = spawn({
    cmd: ["bunx", "cdk8s", "import", fullPath],
    stdout: "inherit",
    stderr: "inherit",
  });
  const code = await proc.exited;
  if (code !== 0) {
    console.error(`❌ Failed to import ${file}`);
    process.exit(code);
  }
}

console.log("✅ All CRDs imported successfully.");
