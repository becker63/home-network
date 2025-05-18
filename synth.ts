import { App } from "cdk8s";
import * as path from "path";
import * as fs from "fs";

const app = new App();

// Read all .ts files in the charts directory (excluding test files or .d.ts)
const chartsDir = path.join(__dirname, "charts");
const chartFiles = fs
  .readdirSync(chartsDir)
  .filter((file) => file.endsWith(".ts") && !file.endsWith(".d.ts"));

// Import each chart module dynamically
for (const file of chartFiles) {
  const modulePath = `./charts/${path.basename(file, ".ts")}`;
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
