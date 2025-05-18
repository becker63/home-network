// TODO refactor ai slop
// prevent it from generating a hash per chat eg: nginxchart-c87fe4d0.k8s
// Alternatively learn how this hash is generated, we need to make sure running synth twice creates the same charts
import fs from "fs";
import path from "path";
import * as yaml from "js-yaml";

const SYNTH_PATH = "./synth_yaml";
const TESTS_PATH = "./kuttl_tests";

const files = fs.readdirSync(SYNTH_PATH).filter((f) => f.endsWith(".yaml"));

type K8sManifest = {
  apiVersion?: string;
  kind?: string;
  metadata?: {
    name?: string;
  };
  [key: string]: any;
};

for (const file of files) {
  const fullPath = path.join(SYNTH_PATH, file);
  const contents = fs.readFileSync(fullPath, "utf8");
  const docs = yaml.loadAll(contents) as K8sManifest[];

  const testName = path.basename(file, ".yaml");
  const testDir = path.join(TESTS_PATH, testName);
  fs.mkdirSync(testDir, { recursive: true });

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
