import * as fs from "fs";
import * as path from "path";
import { spawn } from "bun";

const crdDir = path.resolve("crds");
const importsDir = path.resolve("imports");

if (!fs.existsSync(crdDir)) {
  console.error("❌ crds/ directory does not exist.");
  process.exit(1);
}

const files = fs
  .readdirSync(crdDir)
  .filter((f) => f.endsWith(".yaml"))
  .filter((f) => {
    const group = f
      .replace(/^provider-/, "")
      .replace(/\.yaml$/, "")
      .replace(/_/g, "."); // crude heuristic
    return !fs.existsSync(path.join(importsDir, `${group}.ts`));
  });

if (files.length === 0) {
  console.log("✅ All CRDs already imported.");
  process.exit(0);
}

console.log(`📥 Importing ${files.length} CRDs into CDK8s...`);

const paths = files.map((f) => path.join(crdDir, f));
const proc = spawn({
  cmd: ["bunx", "cdk8s", "import", ...paths],
  stdout: "inherit",
  stderr: "inherit",
});
const code = await proc.exited;

if (code !== 0) {
  console.error("❌ Failed to import some CRDs");
  process.exit(code);
}

console.log("✅ All CRDs imported successfully.");
