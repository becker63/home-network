// TODO refactor ai slop
// prevent it from generating a hash per chat eg: nginxchart-c87fe4d0.k8s
// Alternatively learn how this hash is generated, we need to make sure running synth twice creates the same charts
import fs from "fs";
import path from "path";
import * as yaml from "js-yaml";

const SYNTH_PATH = "./synth_yaml";
const TESTS_PATH = "./kuttl_tests";

type K8sManifest = {
  apiVersion?: string;
  kind?: string;
  metadata?: {
    name?: string;
  };
  [key: string]: any;
};

function walk(dir: string): string[] {
  let files: string[] = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files = files.concat(walk(fullPath));
    } else if (
      entry.isFile() &&
      entry.name.endsWith(".yaml") &&
      !/(\b|[_-])(nt|NT)(\b|[_-])/.test(entry.name)
    ) {
      files.push(fullPath);
    }
  }
  return files;
}

const files = walk(SYNTH_PATH);

for (const fullPath of files) {
  const relPath = path.relative(SYNTH_PATH, fullPath);
  const testName = relPath.replace(/\.yaml$/, "").replace(/\//g, "-");
  const testDir = path.join(TESTS_PATH, testName);
  fs.mkdirSync(testDir, { recursive: true });

  const contents = fs.readFileSync(fullPath, "utf8");
  const docs = yaml.loadAll(contents) as K8sManifest[];

  const applyPath = path.join(testDir, "00-apply.yaml");
  const applyStep = {
    apiVersion: "kuttl.dev/v1beta1",
    kind: "TestStep",
    apply: [path.relative(testDir, fullPath)],
  };
  if (!fs.existsSync(applyPath)) {
    fs.writeFileSync(applyPath, yaml.dump(applyStep));
  }

  const assertions: K8sManifest[] = docs
    .filter((doc) => doc?.kind && doc?.metadata?.name)
    .map((doc) => ({
      apiVersion: doc.apiVersion,
      kind: doc.kind,
      metadata: {
        name: doc.metadata!.name,
      },
    }));

  if (assertions.length > 0) {
    const assertPath = path.join(testDir, "01-assert.yaml");
    if (!fs.existsSync(assertPath)) {
      fs.writeFileSync(
        assertPath,
        assertions.map((doc) => yaml.dump(doc)).join("---\n"),
      );
    }
  }
}
