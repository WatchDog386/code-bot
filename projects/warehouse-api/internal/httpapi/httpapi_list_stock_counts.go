package httpapi

import (
	"net/http"

	"warehouse-api/internal/model"
)

func (a *API) listStockCounts(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListStockCounts()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.StockCounts.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.StockCount) bool { return hits[item.ID] })
	}
	if id, ok, err := queryInt(r, "bin_id"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.StockCount) bool { return item.BinID == id })
	}
	if id, ok, err := queryInt(r, "product_id"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.StockCount) bool { return item.ProductID == id })
	}
	if day := q.Get("counted_from"); day != "" {
		items = keep(items, func(item model.StockCount) bool { return item.Counted >= day })
	}
	if day := q.Get("counted_to"); day != "" {
		items = keep(items, func(item model.StockCount) bool { return item.Counted <= day })
	}
	if limit, ok, err := queryInt(r, "min_expected"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.StockCount) bool { return item.Expected >= limit })
	}
	if limit, ok, err := queryInt(r, "max_expected"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.StockCount) bool { return item.Expected <= limit })
	}
	if limit, ok, err := queryInt(r, "min_found"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.StockCount) bool { return item.Found >= limit })
	}
	if limit, ok, err := queryInt(r, "max_found"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.StockCount) bool { return item.Found <= limit })
	}
	if value := q.Get("counter"); value != "" {
		items = keep(items, func(item model.StockCount) bool { return item.Counter == value })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}
