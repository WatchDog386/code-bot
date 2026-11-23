package httpapi

import (
	"net/http"
	"strconv"

	"warehouse-api/internal/model"
)

func queryBool(r *http.Request, name string) (bool, bool, error) {
	raw := r.URL.Query().Get(name)
	if raw == "" {
		return false, false, nil
	}
	v, err := strconv.ParseBool(raw)
	if err != nil {
		return false, false, &model.ValidationError{Field: name, Message: "must be true or false"}
	}
	return v, true, nil
}

// keep returns the items ok() accepts.
func keep[T any](items []T, ok func(T) bool) []T {
	out := make([]T, 0, len(items))
	for _, item := range items {
		if ok(item) {
			out = append(out, item)
		}
	}
	return out
}
