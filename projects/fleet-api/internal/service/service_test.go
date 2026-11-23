package service_test

import (
	"errors"
	"testing"

	"fleet-api/internal/model"
	"fleet-api/internal/service"
)

func seeded(t *testing.T) *service.Service {
	t.Helper()
	svc := service.New()
	if err := svc.Seed(3); err != nil {
		t.Fatalf("seed: %v", err)
	}
	return svc
}

func wantField(t *testing.T, err error, field string) {
	t.Helper()
	var invalid *model.ValidationError
	if !errors.As(err, &invalid) || invalid.Field != field {
		t.Fatalf("want a validation error on %q, got %v", field, err)
	}
}
