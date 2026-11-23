package service_test

import (
	"bytes"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"library-api/internal/model"
	"library-api/internal/service"
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

func call(t *testing.T, h http.Handler, method, path string, body any) *httptest.ResponseRecorder {
	t.Helper()
	var reader *bytes.Reader
	if body == nil {
		reader = bytes.NewReader(nil)
	} else {
		data, err := json.Marshal(body)
		if err != nil {
			t.Fatalf("marshal: %v", err)
		}
		reader = bytes.NewReader(data)
	}
	rec := httptest.NewRecorder()
	h.ServeHTTP(rec, httptest.NewRequest(method, path, reader))
	return rec
}

// keep the imports used even for domains without text fields
var _ = strings.ToUpper
