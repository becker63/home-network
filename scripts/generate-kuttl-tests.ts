import {
  readFileSync,
  readdirSync,
  mkdirSync,
  existsSync,
  writeFileSync,
  renameSync,
} from "fs";
import { join, relative, basename } from "path";
import * as yaml from "js-yaml";

const SYNTH_PATH = "./synth_yaml";
const TESTS_PATH = "./kuttl_tests";

type K8sManifest = {
  apiVersion?: string;
  kind?: string;
  metadata?: { name?: string };
  [key: string]: any;
};

function walk(dir: string): string[] {
  const files: string[] = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...walk(fullPath));
    } else if (entry.isFile() && fullPath.endsWith(".yaml")) {
      files.push(fullPath);
    }
  }
  return files;
}

console.log("🔍 Walking directory:", SYNTH_PATH);
const allFiles = walk(SYNTH_PATH);
console.log(`📦 Found ${allFiles.length} .yaml file(s) total.`);

// Skip NT test files
const files = allFiles.filter((file) => {
  const name = basename(file);
  return !/nt[_-]/i.test(name);
});

console.log(`🧪 Generating tests for ${files.length} file(s)...`);

for (const fullPath of files) {
  const relPath = relative(SYNTH_PATH, fullPath);
  const filename = basename(relPath, ".yaml"); // e.g. mychart-somehash
  const testPrefix = filename.split("-").slice(0, -1).join("-"); // without hash
  const testDirGlob = readdirSync(TESTS_PATH).find((dir) =>
    dir.startsWith(testPrefix),
  );

  const newTestDir = join(TESTS_PATH, filename);
  const contents = readFileSync(fullPath, "utf8");
  const docs = yaml.loadAll(contents) as K8sManifest[];

  // Move existing test directory if needed
  if (testDirGlob && testDirGlob !== filename) {
    const oldPath = join(TESTS_PATH, testDirGlob);
    renameSync(oldPath, newTestDir);
  } else {
    mkdirSync(newTestDir, { recursive: true });
  }

  const applyPath = join(newTestDir, "00-apply.yaml");
  const applyStep = {
    apiVersion: "kuttl.dev/v1beta1",
    kind: "TestStep",
    apply: [join("..", "..", SYNTH_PATH, relPath)],
  };

  // Always update 00-apply.yaml to reflect new file name
  writeFileSync(applyPath, yaml.dump(applyStep));

  const assertions: K8sManifest[] = docs
    .filter((doc) => doc?.kind && doc?.metadata?.name)
    .map((doc) => ({
      apiVersion: doc.apiVersion,
      kind: doc.kind,
      metadata: { name: doc.metadata!.name },
    }));

  const assertPath = join(newTestDir, "01-assert.yaml");

  if (!existsSync(assertPath) && assertions.length > 0) {
    const assertStep = {
      apiVersion: "kuttl.dev/v1beta1",
      kind: "TestAssert",
      assert: assertions,
    };
    writeFileSync(assertPath, yaml.dump(assertStep));
  }
}

console.log("✅ Test generation complete.");
