package httpapi

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
