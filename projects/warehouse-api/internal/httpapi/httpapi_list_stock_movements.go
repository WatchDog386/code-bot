package httpapi

import (
	"net/http"

	"warehouse-api/internal/model"
)

func (a *API) listStockMovements(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListStockMovements()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.StockMovements.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.StockMovement) bool { return hits[item.ID] })
	}
	if id, ok, err := queryInt(r, "product_id"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.StockMovement) bool { return item.ProductID == id })
	}
	if id, ok, err := queryInt(r, "bin_id"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.StockMovement) bool { return item.BinID == id })
	}
	if limit, ok, err := queryInt(r, "min_quantity"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.StockMovement) bool { return item.Quantity >= limit })
	}
	if limit, ok, err := queryInt(r, "max_quantity"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.StockMovement) bool { return item.Quantity <= limit })
	}
	if day := q.Get("moved_from"); day != "" {
		items = keep(items, func(item model.StockMovement) bool { return item.Moved >= day })
	}
	if day := q.Get("moved_to"); day != "" {
		items = keep(items, func(item model.StockMovement) bool { return item.Moved <= day })
	}
	if raw := q.Get("reason"); raw != "" {
		wanted, err := model.ParseStockMovementReason(raw)
		if err != nil {
			writeError(w, err)
			return
		}
		items = keep(items, func(item model.StockMovement) bool { return item.Reason == wanted })
	}
	if value := q.Get("reference"); value != "" {
		items = keep(items, func(item model.StockMovement) bool { return item.Reference == value })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}
