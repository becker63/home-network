package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"os/exec"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/digitalocean/godo"
	"golang.org/x/oauth2"
)

const (
	imageBuildOutputPath = "./result/qcow2"
	imageOutLink         = "result"
	nixBuildTarget       = ".#nixosConfigurations.vm.config.system.build.qcow2"
	digitalOceanRegion   = "nyc3"
	imageDistribution    = "Unknown"
)

var (
	s3Bucket          = os.Getenv("S3_BUCKET")
	digitalOceanToken = os.Getenv("DIGITALOCEAN_TOKEN")
)

// Entrypoint to build, upload, and register image
func BuildImageAndReturnSlug(ctx context.Context) (string, error) {
	slug := generateSlug()
	imagePath := imageBuildOutputPath

	if err := buildNixImage(); err != nil {
		return "", fmt.Errorf("build failed: %w", err)
	}

	s3URL, err := uploadToS3(ctx, imagePath, slug)
	if err != nil {
		return "", fmt.Errorf("upload failed: %w", err)
	}

	imageSlug, err := registerDOImage(ctx, slug, s3URL)
	if err != nil {
		return "", fmt.Errorf("register failed: %w", err)
	}

	return imageSlug, nil
}

func buildNixImage() error {
	log.Println("🔧 Running nix build")
	cmd := exec.Command("nix", "build", nixBuildTarget, "--out-link", imageOutLink)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}

func generateSlug() string {
	return "nixos-" + time.Now().Format("20060102-150405")
}

func uploadToS3(ctx context.Context, filePath, slug string) (string, error) {
	log.Println("📤 Uploading to S3")

	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		return "", err
	}
	client := s3.NewFromConfig(cfg)

	file, err := os.Open(filePath)
	if err != nil {
		return "", err
	}
	defer file.Close()

	key := slug + ".qcow2"
	_, err = client.PutObject(ctx, &s3.PutObjectInput{
		Bucket: aws.String(s3Bucket),
		Key:    aws.String(key),
		Body:   file,
	})
	if err != nil {
		return "", err
	}

	return fmt.Sprintf("https://%s.s3.amazonaws.com/%s", s3Bucket, key), nil
}

func registerDOImage(ctx context.Context, slug, s3URL string) (string, error) {
	log.Println("🛰️ Registering image with DigitalOcean")

	if digitalOceanToken == "" {
		return "", fmt.Errorf("DIGITALOCEAN_TOKEN environment variable not set")
	}

	ts := &tokenSource{AccessToken: digitalOceanToken}
	do := godo.NewClient(oauth2.NewClient(ctx, ts))

	createRequest := &godo.CustomImageCreateRequest{
		Name:         slug,
		Url:          s3URL,
		Region:       digitalOceanRegion,
		Distribution: imageDistribution,
	}

	image, _, err := do.Images.Create(ctx, createRequest)
	if err != nil {
		return "", fmt.Errorf("failed to create custom image: %w", err)
	}

	return image.Slug, nil
}

type tokenSource struct {
	AccessToken string
}

func (t *tokenSource) Token() (*oauth2.Token, error) {
	return &oauth2.Token{AccessToken: t.AccessToken}, nil
}
