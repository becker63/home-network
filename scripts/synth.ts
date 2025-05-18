// scripts/synth.ts
import { App } from "cdk8s";
import * as path from "path";
import * as fs from "fs";

const app = new App();

// Resolve charts directory relative to the project root
const chartsDir = path.join(process.cwd(), "charts");

const chartFiles = fs
  .readdirSync(chartsDir)
  .filter((file) => file.endsWith(".ts") && !file.endsWith(".d.ts"));

for (const file of chartFiles) {
  const modulePath = path.join(chartsDir, path.basename(file, ".ts"));
  const mod = require(modulePath);

  for (const exportName of Object.keys(mod)) {
    const ExportedChart = mod[exportName];

    if (typeof ExportedChart === "function") {
      try {
        new ExportedChart(app, exportName);
      } catch (e) {
        console.warn(`Skipping ${exportName}: ${e}`);
      }
    }
  }
}

app.synth();
