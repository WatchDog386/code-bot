package httpapi

import (
	"crypto/rand"
	"encoding/hex"
	"log"
	"net/http"
	"strconv"
	"sync/atomic"
)

var fallbackRequestID atomic.Uint64

// withRequestContext adds a fresh request identifier and keeps handler panics from
// terminating the server process.
func withRequestContext(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		id := requestID()
		w.Header().Set("X-Request-ID", id)
		defer func() {
			if recovered := recover(); recovered != nil {
				log.Printf("request %s panicked: %v", id, recovered)
				writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "internal server error", "request_id": id})
			}
		}()
		next.ServeHTTP(w, r)
	})
}

func requestID() string {
	var value [12]byte
	if _, err := rand.Read(value[:]); err == nil {
		return hex.EncodeToString(value[:])
	}
	return "fallback-" + strconv.FormatUint(fallbackRequestID.Add(1), 10)
}
