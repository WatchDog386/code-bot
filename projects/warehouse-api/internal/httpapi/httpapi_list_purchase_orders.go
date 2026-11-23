package httpapi

import (
	"net/http"

	"warehouse-api/internal/model"
)

func (a *API) listPurchaseOrders(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListPurchaseOrders()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.PurchaseOrders.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.PurchaseOrder) bool { return hits[item.ID] })
	}
	if id, ok, err := queryInt(r, "supplier_id"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.PurchaseOrder) bool { return item.SupplierID == id })
	}
	if day := q.Get("ordered_from"); day != "" {
		items = keep(items, func(item model.PurchaseOrder) bool { return item.Ordered >= day })
	}
	if day := q.Get("ordered_to"); day != "" {
		items = keep(items, func(item model.PurchaseOrder) bool { return item.Ordered <= day })
	}
	if day := q.Get("expected_from"); day != "" {
		items = keep(items, func(item model.PurchaseOrder) bool { return item.Expected >= day })
	}
	if day := q.Get("expected_to"); day != "" {
		items = keep(items, func(item model.PurchaseOrder) bool { return item.Expected <= day })
	}
	if limit, ok, err := queryFloat(r, "min_total"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.PurchaseOrder) bool { return item.Total >= limit })
	}
	if limit, ok, err := queryFloat(r, "max_total"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.PurchaseOrder) bool { return item.Total <= limit })
	}
	if raw := q.Get("status"); raw != "" {
		wanted, err := model.ParsePurchaseOrderStatus(raw)
		if err != nil {
			writeError(w, err)
			return
		}
		items = keep(items, func(item model.PurchaseOrder) bool { return item.Status == wanted })
	}
	if value := q.Get("notes"); value != "" {
		items = keep(items, func(item model.PurchaseOrder) bool { return item.Notes == value })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}
