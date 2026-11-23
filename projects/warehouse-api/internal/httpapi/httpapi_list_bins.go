package httpapi

import (
	"net/http"

	"warehouse-api/internal/model"
)

func (a *API) listBins(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListBins()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.Bins.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.Bin) bool { return hits[item.ID] })
	}
	if value := q.Get("code"); value != "" {
		items = keep(items, func(item model.Bin) bool { return item.Code == value })
	}
	if value := q.Get("aisle"); value != "" {
		items = keep(items, func(item model.Bin) bool { return item.Aisle == value })
	}
	if limit, ok, err := queryInt(r, "min_shelf"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Bin) bool { return item.Shelf >= limit })
	}
	if limit, ok, err := queryInt(r, "max_shelf"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Bin) bool { return item.Shelf <= limit })
	}
	if limit, ok, err := queryInt(r, "min_capacity"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Bin) bool { return item.Capacity >= limit })
	}
	if limit, ok, err := queryInt(r, "max_capacity"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Bin) bool { return item.Capacity <= limit })
	}
	if flag, ok, err := queryBool(r, "refrigerated"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Bin) bool { return item.Refrigerated == flag })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}
