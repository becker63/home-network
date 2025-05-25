import { App } from "cdk8s";
import * as path from "path";
import * as fs from "fs";

const app = new App();

function walk(dir: string): string[] {
  let files: string[] = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files = files.concat(walk(fullPath));
    } else if (
      entry.isFile() &&
      entry.name.endsWith(".ts") &&
      !entry.name.endsWith(".d.ts")
    ) {
      files.push(fullPath);
    }
  }
  return files;
}

const chartsDir = path.join(process.cwd(), "charts");
console.log(`🔍 Searching for charts in: ${chartsDir}`);
const chartFiles = walk(chartsDir);

console.log(`📦 Found ${chartFiles.length} chart file(s).`);

const usedIds = new Set<string>();

for (const file of chartFiles) {
  console.log(`\n📄 Processing file: ${file}`);

  if (/lib/i.test(file)) {
    console.log(`⏭️ Skipping file (lib): ${file}`);
    continue;
  }

  let mod;
  try {
    mod = require(file);
  } catch (e) {
    console.error(`❌ Failed to require file: ${file}\n${e}`);
    continue;
  }

  const exportNames = Object.keys(mod);
  if (exportNames.length === 0) {
    console.warn(`⚠️ No exports found in: ${file}`);
    continue;
  }

  for (const exportName of exportNames) {
    if (/lib/i.test(exportName)) {
      console.log(`⏭️ Skipping export (lib): ${exportName}`);
      continue;
    }

    const ExportedChart = mod[exportName];
    if (typeof ExportedChart === "function") {
      try {
        new ExportedChart(app, exportName); // <== use exportName directly
        console.log(`✅ Synthesized chart: ${exportName}`);
      } catch (e) {
        console.warn(`⚠️ Skipping chart ${exportName}: ${e}`);
      }
    } else {
      console.log(`⏭️ Skipping non-function export: ${exportName}`);
    }
  }
}

console.log(`\n🚀 Running app.synth()...`);
app.synth();
console.log(`🎉 Synthesis complete.`);
