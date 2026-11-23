package httpapi

import (
	"net/http"

	"warehouse-api/internal/model"
)

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

func (a *API) listSuppliers(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListSuppliers()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.Suppliers.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.Supplier) bool { return hits[item.ID] })
	}
	if value := q.Get("name"); value != "" {
		items = keep(items, func(item model.Supplier) bool { return item.Name == value })
	}
	if value := q.Get("email"); value != "" {
		items = keep(items, func(item model.Supplier) bool { return item.Email == value })
	}
	if value := q.Get("phone"); value != "" {
		items = keep(items, func(item model.Supplier) bool { return item.Phone == value })
	}
	if value := q.Get("country"); value != "" {
		items = keep(items, func(item model.Supplier) bool { return item.Country == value })
	}
	if limit, ok, err := queryInt(r, "min_lead_days"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Supplier) bool { return item.LeadDays >= limit })
	}
	if limit, ok, err := queryInt(r, "max_lead_days"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Supplier) bool { return item.LeadDays <= limit })
	}
	if flag, ok, err := queryBool(r, "preferred"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Supplier) bool { return item.Preferred == flag })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}
