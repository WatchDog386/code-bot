package httpapi

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestRequestContextAddsID(t *testing.T) {
	handler := withRequestContext(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusNoContent)
	}))
	response := httptest.NewRecorder()
	handler.ServeHTTP(response, httptest.NewRequest(http.MethodGet, "/", nil))
	if response.Code != http.StatusNoContent || response.Header().Get("X-Request-ID") == "" {
		t.Fatalf("response = %d, request ID %q", response.Code, response.Header().Get("X-Request-ID"))
	}
}

func TestRequestContextRecoversPanic(t *testing.T) {
	handler := withRequestContext(http.HandlerFunc(func(http.ResponseWriter, *http.Request) { panic("broken handler") }))
	response := httptest.NewRecorder()
	handler.ServeHTTP(response, httptest.NewRequest(http.MethodGet, "/", nil))
	if response.Code != http.StatusInternalServerError || response.Header().Get("X-Request-ID") == "" {
		t.Fatalf("response = %d, body %q", response.Code, response.Body.String())
	}
}
