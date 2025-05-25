import simpleGit from "simple-git";
import * as fs from "fs";
import * as path from "path";

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error("❌ No submodules provided. Usage: name=url name2=url2");
  process.exit(1);
}

const git = simpleGit();
const baseDir = path.resolve("crossplane-providers");
fs.mkdirSync(baseDir, { recursive: true });

// Check .gitmodules for registered submodules
const gitmodulesPath = path.resolve(".gitmodules");
const gitmodules = fs.existsSync(gitmodulesPath)
  ? fs.readFileSync(gitmodulesPath, "utf-8")
  : "";

// Get Git index entries
const indexPaths = new Set(
  (await git.raw(["ls-files"])).split("\n").map((line) => line.trim()),
);

for (const arg of args) {
  const [name, url] = arg.split("=");

  if (!name || !url) {
    console.error(`❌ Invalid format: '${arg}'. Use name=url`);
    process.exit(1);
  }

  const submodulePath = `crossplane-providers/${name}`;

  const inGitmodules = gitmodules.includes(`[submodule "${submodulePath}"]`);
  const inIndex = indexPaths.has(submodulePath);

  if (inGitmodules) {
    console.log(`✅ Submodule '${name}' already registered`);
    continue;
  }

  if (inIndex) {
    console.warn(
      `⚠️  '${submodulePath}' exists in Git index but is not a valid submodule.`,
    );
    console.warn(
      `💡 Run 'git rm --cached ${submodulePath}' to remove and try again.`,
    );
    continue;
  }

  try {
    console.log(`➕ Adding submodule '${name}'`);
    await git.subModule(["add", url, submodulePath]);
  } catch (err) {
    console.error(`❌ Failed to add submodule '${name}'`, err);
  }
}

console.log("🔄 Initializing submodules...");
await git.subModule(["update", "--init", "--recursive"]);
console.log("✅ All submodules initialized.");
