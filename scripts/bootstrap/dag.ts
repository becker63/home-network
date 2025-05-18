import { graphStratify } from "d3-dag";

type Task = {
  name: string;
  run: () => Promise<void> | void;
  dependsOn?: string[];
};

type DagDefinition = {
  tasks: Task[];
};

export async function defineDag({ tasks }: DagDefinition): Promise<void> {
  const taskMap = new Map<string, Task>();
  for (const task of tasks) {
    if (taskMap.has(task.name)) throw new Error(`Duplicate task: ${task.name}`);
    taskMap.set(task.name, task);
  }

  const stratify = graphStratify()
    .id((d: Task) => d.name)
    .parentIds((d: Task) => d.dependsOn ?? []);

  stratify(tasks);

  // 🔍 Build a child map for visualization
  const childMap = new Map<string, string[]>();
  for (const task of tasks) {
    for (const parent of task.dependsOn ?? []) {
      if (!childMap.has(parent)) childMap.set(parent, []);
      childMap.get(parent)!.push(task.name);
    }
  }

  // 🔠 Find root nodes (tasks with no dependencies)
  const roots = tasks
    .filter((t) => !t.dependsOn || t.dependsOn.length === 0)
    .map((t) => t.name);

  // 🖼️ Print ASCII Tree recursively
  function printTree(
    node: string,
    prefix = "",
    isLast = true,
    seen = new Set<string>(),
  ) {
    const connector = isLast ? "└── " : "├── ";

    if (seen.has(node)) {
      console.log(prefix + connector + node + " (↩)");
      return;
    }

    console.log(prefix + connector + node);
    seen.add(node);

    const children = childMap.get(node) ?? [];
    const nextPrefix = prefix + (isLast ? "    " : "│   ");

    children.forEach((child, index) => {
      const last = index === children.length - 1;
      printTree(child, nextPrefix, last, seen);
    });
  }

  console.log("📊 DAG Structure:");
  roots.forEach((root, index) => {
    const isLast = index === roots.length - 1;
    printTree(root, "", isLast);
  });
  console.log("");

  // Topological sort
  const sorted: string[] = [];
  const visited = new Set<string>();

  function visit(nodeId: string) {
    if (visited.has(nodeId)) return;
    visited.add(nodeId);

    const task = taskMap.get(nodeId);
    const deps = task?.dependsOn ?? [];
    for (const dep of deps) {
      visit(dep);
    }

    sorted.push(nodeId);
  }

  for (const task of tasks) {
    visit(task.name);
  }

  // Execute tasks in order
  for (const name of sorted) {
    const task = taskMap.get(name)!;
    console.log(`▶️ Running task: ${name}`);
    await task.run();
  }

  console.log("✅ DAG execution complete.");
}
