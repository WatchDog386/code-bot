package service_test

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"testing"

	"library-api/internal/httpapi"
	"library-api/internal/model"
	"library-api/internal/service"
)

func TestAuthorAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/authors", service.SampleAuthor(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.Author
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/authors/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/authors?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/authors/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/authors", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}

func TestBookCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateBook(service.SampleBook(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetBook(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListBooks()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestBookMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetBook(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}
