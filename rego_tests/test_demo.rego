package rego_tests

import data.lib.kubernetes

deny contains msg if {
	kubernetes.is_deployment
	container := kubernetes.containers[_]
	endswith(container.image, ":latest")
	msg := sprintf("Container '%s' uses the 'latest' tag", [container.name])
}

deny contains msg if {
	kubernetes.is_deployment
	container := kubernetes.containers[_]
	not container.resources
	msg := sprintf("Container '%s' is missing resource definitions", [container.name])
}

deny contains msg if {
	kubernetes.is_deployment
	container := kubernetes.containers[_]
	not container.resources.limits
	msg := sprintf("Container '%s' is missing resource limits", [container.name])
}

deny contains msg if {
	kubernetes.is_deployment
	container := kubernetes.containers[_]
	not container.resources.requests
	msg := sprintf("Container '%s' is missing resource requests", [container.name])
}
