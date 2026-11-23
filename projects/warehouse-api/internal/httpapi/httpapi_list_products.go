package httpapi

import (
	"net/http"

	"warehouse-api/internal/model"
)

func (a *API) listProducts(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListProducts()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.Products.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.Product) bool { return hits[item.ID] })
	}
	if id, ok, err := queryInt(r, "supplier_id"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Product) bool { return item.SupplierID == id })
	}
	if value := q.Get("sku"); value != "" {
		items = keep(items, func(item model.Product) bool { return item.Sku == value })
	}
	if value := q.Get("name"); value != "" {
		items = keep(items, func(item model.Product) bool { return item.Name == value })
	}
	if limit, ok, err := queryFloat(r, "min_unit_cost"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Product) bool { return item.UnitCost >= limit })
	}
	if limit, ok, err := queryFloat(r, "max_unit_cost"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Product) bool { return item.UnitCost <= limit })
	}
	if limit, ok, err := queryFloat(r, "min_unit_price"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Product) bool { return item.UnitPrice >= limit })
	}
	if limit, ok, err := queryFloat(r, "max_unit_price"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Product) bool { return item.UnitPrice <= limit })
	}
	if limit, ok, err := queryInt(r, "min_reorder_level"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Product) bool { return item.ReorderLevel >= limit })
	}
	if limit, ok, err := queryInt(r, "max_reorder_level"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Product) bool { return item.ReorderLevel <= limit })
	}
	if raw := q.Get("category"); raw != "" {
		wanted, err := model.ParseProductCategory(raw)
		if err != nil {
			writeError(w, err)
			return
		}
		items = keep(items, func(item model.Product) bool { return item.Category == wanted })
	}
	if flag, ok, err := queryBool(r, "active"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Product) bool { return item.Active == flag })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}
