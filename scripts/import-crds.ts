import * as fs from "fs";
import * as path from "path";
import { spawn } from "bun";
import * as yaml from "yaml";

const crdDir = path.resolve("crds");
const importsDir = path.resolve("imports");

if (!fs.existsSync(crdDir)) {
  console.error("❌ crds/ directory does not exist.");
  process.exit(1);
}

const files = fs.readdirSync(crdDir).filter((f) => f.endsWith(".yaml"));

if (files.length === 0) {
  console.log("✅ No CRDs to import.");
  process.exit(0);
}

console.log(`📥 Importing ${files.length} CRDs into CDK8s...`);

for (const file of files) {
  const crdPath = path.join(crdDir, file);
  const crdYaml = fs.readFileSync(crdPath, "utf8");
  const docs = yaml.parseAllDocuments(crdYaml);
  const parsed = docs[0].toJSON(); // Use first document

  const group = parsed?.spec?.group ?? "unknown";
  const kind = parsed?.spec?.names?.kind ?? "UnknownKind";
  const filename = `${group}.${kind}.ts`;
  const importPath = path.join(importsDir, filename);

  if (fs.existsSync(importPath)) {
    console.log(`⚠️ Skipping already imported: ${filename}`);
    continue;
  }

  console.log(`🔄 Importing ${file} → ${filename}`);

  const proc = spawn({
    cmd: [
      "bunx",
      "cdk8s",
      "import",
      "--language",
      "typescript",
      "-o",
      importsDir,
      crdPath,
    ],
    stdout: "inherit",
    stderr: "inherit",
  });

  const code = await proc.exited;
  if (code !== 0) {
    console.error(`❌ Failed to import ${file}`);
    process.exit(code);
  }

  // Rename the output file
  const defaultName = `${group}.ts`;
  const defaultPath = path.join(importsDir, defaultName);
  if (fs.existsSync(defaultPath)) {
    fs.renameSync(defaultPath, importPath);
  }
}

console.log("✅ All CRDs imported successfully.");
