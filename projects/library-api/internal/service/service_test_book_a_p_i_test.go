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

func TestBookAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/books", service.SampleBook(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.Book
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/books/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/books?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/books/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/books", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}

func TestMemberCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateMember(service.SampleMember(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetMember(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListMembers()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestMemberMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetMember(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestMemberRejectsBadName(t *testing.T) {
	svc := seeded(t)
	item := service.SampleMember(12)
	item.Name = ""
	_, err := svc.CreateMember(item)
	wantField(t, err, "name")
}

func TestMemberRejectsBadEmail(t *testing.T) {
	svc := seeded(t)
	item := service.SampleMember(12)
	item.Email = "not-an-email"
	_, err := svc.CreateMember(item)
	wantField(t, err, "email")
}

func TestMemberRejectsBadPhone(t *testing.T) {
	svc := seeded(t)
	item := service.SampleMember(12)
	item.Phone = ""
	_, err := svc.CreateMember(item)
	wantField(t, err, "phone")
}
