import * as fs from "fs";
import { spawn } from "bun";

export function assertDirExists(dir: string): void {
  if (!fs.existsSync(dir) || !fs.statSync(dir).isDirectory()) {
    console.error(`❌ Directory does not exist: ${dir}`);
    process.exit(1);
  }
}

export async function runCommand(cmd: string[], cwd: string) {
  const proc = spawn({ cmd, cwd, stdout: "inherit", stderr: "inherit" });
  const exitCode = await proc.exited;
  if (exitCode !== 0) {
    throw new Error(`❌ Command failed: ${cmd.join(" ")}`);
  }
}
