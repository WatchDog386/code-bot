package service_test

import (
	"encoding/json"
	"fmt"
	"net/http"
	"testing"

	"library-api/internal/httpapi"
	"library-api/internal/model"
	"library-api/internal/service"
)

func TestMemberAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/members", service.SampleMember(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.Member
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/members/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/members?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/members/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/members", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}
