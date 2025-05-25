import * as fs from "fs";
import * as path from "path";
import { assertDirExists, runCommand } from "./helpers";

function copyCrds(providerPath: string) {
  const sourceDir = path.resolve(providerPath, "package", "crds");
  const targetDir = path.resolve("crds");

  assertDirExists(sourceDir);
  fs.mkdirSync(targetDir, { recursive: true });

  const files = fs.readdirSync(sourceDir).filter((f) => f.endsWith(".yaml"));
  for (const file of files) {
    const src = path.join(sourceDir, file);
    const dest = path.join(targetDir, `${path.basename(providerPath)}-${file}`);
    fs.copyFileSync(src, dest);
    console.log(`📥 Copied ${file} → ${dest}`);
  }
}

export async function buildProvider(providerPath: string) {
  const absPath = path.resolve(providerPath);
  assertDirExists(absPath);

  console.log(`📦 Building Upjet provider in: ${absPath}`);

  // 🔧 Submodule support not yet available in isomorphic-git
  console.log("🔁 Updating git submodules...");
  await runCommand(
    ["git", "submodule", "update", "--init", "--recursive"],
    absPath,
  );

  console.log("🔨 Running make generate.init...");
  await runCommand(["make", "generate.init"], absPath);

  console.log("📄 Copying CRDs to ./crds/...");
  copyCrds(absPath);

  console.log(`✅ Provider build complete: ${providerPath}`);
}

const [, , providerArg] = process.argv;
if (providerArg) {
  await buildProvider(providerArg);
}
