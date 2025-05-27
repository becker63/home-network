package main

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"

	v1 "github.com/fatedier/frp/pkg/config/v1"
	"github.com/invopop/jsonschema"
)

// generateSchema generates a deduplicated JSON schema from a Go struct and saves it.
func generateSchema(filepath string, example interface{}) error {
	schema := jsonschema.Reflect(example)

	rawBytes, err := json.Marshal(schema)
	if err != nil {
		return fmt.Errorf("failed to marshal schema: %w", err)
	}

	var normalized map[string]interface{}
	if err := json.Unmarshal(rawBytes, &normalized); err != nil {
		return fmt.Errorf("failed to unmarshal for deduplication: %w", err)
	}

	file, err := os.Create(filepath)
	if err != nil {
		return fmt.Errorf("failed to create schema file: %w", err)
	}
	defer file.Close()

	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(normalized); err != nil {
		return fmt.Errorf("failed to write cleaned schema: %w", err)
	}

	return nil
}

func runKCLModInit(dir string) error {
	cmd := exec.Command("kcl", "mod", "init")
	cmd.Dir = dir
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("failed to run 'kcl mod init' in %s: %w", dir, err)
	}
	return nil
}

func removeMainK(dir string) error {
	mainKPath := filepath.Join(dir, "main.k")
	err := os.Remove(mainKPath)
	if err != nil && !os.IsNotExist(err) {
		return fmt.Errorf("failed to remove %s: %w", mainKPath, err)
	}
	return nil
}

func runKCLImport(schemaFile string, dir string) error {
	cmd := exec.Command("kcl", "import", "-m", "jsonschema", schemaFile, "--force")
	cmd.Dir = dir
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("failed to run kcl import on %s in %s: %w", schemaFile, dir, err)
	}
	return nil
}

func ensureDir(dir string) error {
	if err := os.MkdirAll(dir, 0755); err != nil {
		return fmt.Errorf("failed to create directory %s: %w", dir, err)
	}
	return nil
}

func handleSchema(dir string, filename string, example interface{}) error {
	if err := ensureDir(dir); err != nil {
		return err
	}

	if err := runKCLModInit(dir); err != nil {
		return err
	}

	if err := removeMainK(dir); err != nil {
		return err
	}

	schemaPath := filepath.Join(dir, filename)
	if err := generateSchema(schemaPath, example); err != nil {
		return fmt.Errorf("failed to generate schema %s: %w", schemaPath, err)
	}

	if err := runKCLImport(filename, dir); err != nil {
		return fmt.Errorf("kcl import failed in %s: %w", dir, err)
	}

	return nil
}

func main() {
	fmt.Println("Generating kcl for FRP")

	if err := handleSchema("frpc", "frpc.schema.json", &v1.ClientConfig{}); err != nil {
		fmt.Fprintln(os.Stderr, err)
	}

	if err := handleSchema("frps", "frps.schema.json", &v1.ServerConfig{}); err != nil {
		fmt.Fprintln(os.Stderr, err)
	}

	fmt.Println("Done!")
}
