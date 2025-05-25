import {
  readFileSync,
  readdirSync,
  mkdirSync,
  existsSync,
  writeFileSync,
} from "fs";
import { join, relative, basename } from "path";
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
  const files: string[] = [];

  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...walk(fullPath));
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
  const relPath = relative(SYNTH_PATH, fullPath);
  const testName = relPath.replace(/\.yaml$/, "").replace(/\//g, "-");
  const testDir = join(TESTS_PATH, testName);
  mkdirSync(testDir, { recursive: true });

  const contents = readFileSync(fullPath, "utf8");
  const docs = yaml.loadAll(contents) as K8sManifest[];

  // 00-apply.yaml
  const applyPath = join(testDir, "00-apply.yaml");
  const applyStep = {
    apiVersion: "kuttl.dev/v1beta1",
    kind: "TestStep",
    apply: [join("..", "..", SYNTH_PATH, relPath)],
  };

  if (!existsSync(applyPath)) {
    writeFileSync(applyPath, yaml.dump(applyStep));
  }

  // 01-assert.yaml
  const assertions: K8sManifest[] = docs
    .filter((doc) => doc?.kind && doc?.metadata?.name)
    .map((doc) => ({
      apiVersion: doc.apiVersion,
      kind: doc.kind,
      metadata: {
        name: doc.metadata!.name,
      },
    }));

  const assertPath = join(testDir, "01-assert.yaml");
  if (assertions.length > 0 && !existsSync(assertPath)) {
    writeFileSync(
      assertPath,
      [
        {
          apiVersion: "kuttl.dev/v1beta1",
          kind: "TestAssert",
          assert: assertions,
        },
      ]
        .map((doc) => yaml.dump(doc))
        .join("---\n"),
    );
  }
}
