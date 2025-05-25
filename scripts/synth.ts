// scripts/synth.ts
import { App } from "cdk8s";
import * as path from "path";
import * as fs from "fs";

const app = new App();

// Recursively walk a directory and return all .ts files (excluding .d.ts)
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

const chartsDir: string = path.join(process.cwd(), "charts");
const chartFiles: string[] = walk(chartsDir);

console.log(`⛏ Found ${chartFiles.length} chart files`);

for (const file of chartFiles) {
  const mod = require(file);

  for (const exportName of Object.keys(mod)) {
    const ExportedChart = mod[exportName];

    if (typeof ExportedChart === "function") {
      try {
        new ExportedChart(app, exportName);
        console.log(`✅ Synthesized: ${exportName}`);
      } catch (e) {
        console.warn(`⚠️ Skipping ${exportName}: ${e}`);
      }
    }
  }
}

app.synth();
