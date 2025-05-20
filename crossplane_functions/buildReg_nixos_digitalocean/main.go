package main

import (
	"context"

	"github.com/crossplane/function-sdk-go/errors"
	"github.com/crossplane/function-sdk-go/logging"
	v1 "github.com/crossplane/function-sdk-go/proto/v1"
	"github.com/crossplane/function-sdk-go/response"
	"google.golang.org/protobuf/types/known/structpb"
)

type Function struct {
	v1.UnimplementedFunctionRunnerServiceServer
	log logging.Logger
}

func (f *Function) RunFunction(ctx context.Context, req *v1.RunFunctionRequest) (*v1.RunFunctionResponse, error) {
	f.log.Info("Running Nix Image Builder", "tag", req.GetMeta().GetTag())
	rsp := response.To(req, response.DefaultTTL)

	imageSlug, err := BuildImageAndReturnSlug(ctx)
	if err != nil {
		response.Fatal(rsp, errors.Wrap(err, "image build workflow failed"))
		return rsp, nil
	}

	// Set imageSlug into the function context
	rsp.Context = &structpb.Struct{
		Fields: map[string]*structpb.Value{
			"imageSlug": structpb.NewStringValue(imageSlug),
		},
	}

	response.ConditionTrue(rsp, "FunctionSuccess", "ImageSlugStoredInContext").
		TargetCompositeAndClaim()

	f.log.Info("✅ Stored imageSlug in function context", "slug", imageSlug)
	return rsp, nil
}
