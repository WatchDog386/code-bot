package api

import (
	"encoding/json"
	"errors"
	"log/slog"
	"net/http"
	"time"

	"github.com/example/link-shortener/internal/shortener"
	"github.com/example/link-shortener/internal/store"
)

type Handler struct {
	svc     *shortener.Service
	baseURL string
	log     *slog.Logger
}

func NewHandler(svc *shortener.Service, baseURL string, log *slog.Logger) *Handler {
	return &Handler{svc: svc, baseURL: baseURL, log: log}
}

type shortenRequest struct {
	URL        string `json:"url"`
	TTLMinutes int    `json:"ttl_minutes"`
}

type shortenResponse struct {
	Code     string `json:"code"`
	ShortURL string `json:"short_url"`
}

func (h *Handler) Routes() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("POST /api/links", h.shorten)
	mux.HandleFunc("GET /{code}", h.redirect)
	mux.HandleFunc("GET /healthz", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	})
	return h.logRequests(mux)
}

func (h *Handler) shorten(w http.ResponseWriter, r *http.Request) {
	var req shortenRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid json body")
		return
	}

	ttl := time.Duration(req.TTLMinutes) * time.Minute
	link, err := h.svc.Shorten(req.URL, ttl)
	if errors.Is(err, shortener.ErrInvalidURL) {
		writeError(w, http.StatusUnprocessableEntity, err.Error())
		return
	}
	if err != nil {
		h.log.Error("shorten failed", "err", err)
		writeError(w, http.StatusInternalServerError, "internal error")
		return
	}

	writeJSON(w, http.StatusCreated, shortenResponse{
		Code:     link.Code,
		ShortURL: h.baseURL + "/" + link.Code,
	})
}

func (h *Handler) redirect(w http.ResponseWriter, r *http.Request) {
	target, err := h.svc.Resolve(r.PathValue("code"))
	if errors.Is(err, store.ErrNotFound) {
		http.NotFound(w, r)
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "internal error")
		return
	}
	http.Redirect(w, r, target, http.StatusFound)
}

func (h *Handler) logRequests(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		next.ServeHTTP(w, r)
		h.log.Info("request", "method", r.Method, "path", r.URL.Path, "took", time.Since(start))
	})
}

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}

func writeError(w http.ResponseWriter, status int, msg string) {
	writeJSON(w, status, map[string]string{"error": msg})
}
