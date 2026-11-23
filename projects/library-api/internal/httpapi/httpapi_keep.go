package httpapi

import "net/http"

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

// window returns one page of items (?page= from 1, ?size= up to 200).
func window[T any](r *http.Request, items []T) ([]T, error) {
	page, ok, err := queryInt(r, "page")
	if err != nil {
		return nil, err
	}
	if !ok || page < 1 {
		page = 1
	}
	size, ok, err := queryInt(r, "size")
	if err != nil {
		return nil, err
	}
	if !ok || size < 1 || size > 200 {
		size = 50
	}
	start := (page - 1) * size
	if start >= len(items) {
		return []T{}, nil
	}
	end := min(start+size, len(items))
	return items[start:end], nil
}
