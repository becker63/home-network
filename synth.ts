// scripts/synth.ts
import { App } from "cdk8s";
import { DemoTestChart } from "./charts/test_demo";

const app = new App();
new DemoTestChart(app, "demo-test");
app.synth();
