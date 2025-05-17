package main

# Disallow containers using the "latest" image tag
deny[msg] {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  endswith(container.image, ":latest")
  msg := sprintf("Container '%s' uses the 'latest' tag", [container.name])
}

# Require resource limits
deny[msg] {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]

  not container.resources
  msg := sprintf("Container '%s' is missing resource definitions", [container.name])
}

deny[msg] {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]

  not container.resources.limits
  msg := sprintf("Container '%s' is missing resource limits", [container.name])
}

deny[msg] {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]

  not container.resources.requests
  msg := sprintf("Container '%s' is missing resource requests", [container.name])
}
