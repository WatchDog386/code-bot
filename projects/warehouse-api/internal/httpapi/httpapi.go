// Package httpapi serves the Warehouse Inventory service as JSON over HTTP (net/http only).
//
// Every collection has GET (list, with filters, ?q= search, ?page=&size=), POST,
// GET /{id}, PATCH /{id}, DELETE /{id} and GET /stats.
package httpapi

import (
	"encoding/json"
	"errors"
	"net/http"
	"strconv"

	"warehouse-api/internal/model"
	"warehouse-api/internal/service"
)

// API answers HTTP requests using the service.
type API struct {
	svc *service.Service
}

// New returns the routes of the whole service.
func New(svc *service.Service) http.Handler {
	a := &API{svc: svc}
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", func(w http.ResponseWriter, _ *http.Request) {
		writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
	})
	mux.HandleFunc("GET /suppliers", a.listSuppliers)
	mux.HandleFunc("POST /suppliers", a.createSupplier)
	mux.HandleFunc("GET /suppliers/stats", a.statsSupplier)
	mux.HandleFunc("GET /suppliers/{id}", a.getSupplier)
	mux.HandleFunc("PATCH /suppliers/{id}", a.updateSupplier)
	mux.HandleFunc("DELETE /suppliers/{id}", a.deleteSupplier)
	mux.HandleFunc("GET /products", a.listProducts)
	mux.HandleFunc("POST /products", a.createProduct)
	mux.HandleFunc("GET /products/stats", a.statsProduct)
	mux.HandleFunc("GET /products/{id}", a.getProduct)
	mux.HandleFunc("PATCH /products/{id}", a.updateProduct)
	mux.HandleFunc("DELETE /products/{id}", a.deleteProduct)
	mux.HandleFunc("GET /bins", a.listBins)
	mux.HandleFunc("POST /bins", a.createBin)
	mux.HandleFunc("GET /bins/stats", a.statsBin)
	mux.HandleFunc("GET /bins/{id}", a.getBin)
	mux.HandleFunc("PATCH /bins/{id}", a.updateBin)
	mux.HandleFunc("DELETE /bins/{id}", a.deleteBin)
	mux.HandleFunc("GET /stock-movements", a.listStockMovements)
	mux.HandleFunc("POST /stock-movements", a.createStockMovement)
	mux.HandleFunc("GET /stock-movements/stats", a.statsStockMovement)
	mux.HandleFunc("GET /stock-movements/{id}", a.getStockMovement)
	mux.HandleFunc("PATCH /stock-movements/{id}", a.updateStockMovement)
	mux.HandleFunc("DELETE /stock-movements/{id}", a.deleteStockMovement)
	mux.HandleFunc("GET /purchase-orders", a.listPurchaseOrders)
	mux.HandleFunc("POST /purchase-orders", a.createPurchaseOrder)
	mux.HandleFunc("GET /purchase-orders/stats", a.statsPurchaseOrder)
	mux.HandleFunc("GET /purchase-orders/{id}", a.getPurchaseOrder)
	mux.HandleFunc("PATCH /purchase-orders/{id}", a.updatePurchaseOrder)
	mux.HandleFunc("DELETE /purchase-orders/{id}", a.deletePurchaseOrder)
	mux.HandleFunc("GET /stock-counts", a.listStockCounts)
	mux.HandleFunc("POST /stock-counts", a.createStockCount)
	mux.HandleFunc("GET /stock-counts/stats", a.statsStockCount)
	mux.HandleFunc("GET /stock-counts/{id}", a.getStockCount)
	mux.HandleFunc("PATCH /stock-counts/{id}", a.updateStockCount)
	mux.HandleFunc("DELETE /stock-counts/{id}", a.deleteStockCount)
	mux.HandleFunc("GET /documents", a.listDocuments)
	mux.HandleFunc("POST /documents", a.createDocument)
	mux.HandleFunc("GET /documents/stats", a.statsDocument)
	mux.HandleFunc("GET /documents/{id}", a.getDocument)
	mux.HandleFunc("PATCH /documents/{id}", a.updateDocument)
	mux.HandleFunc("DELETE /documents/{id}", a.deleteDocument)
	mux.HandleFunc("GET /notifications", a.listNotifications)
	mux.HandleFunc("POST /notifications", a.createNotification)
	mux.HandleFunc("GET /notifications/stats", a.statsNotification)
	mux.HandleFunc("GET /notifications/{id}", a.getNotification)
	mux.HandleFunc("PATCH /notifications/{id}", a.updateNotification)
	mux.HandleFunc("DELETE /notifications/{id}", a.deleteNotification)
	return mux
}

func writeJSON(w http.ResponseWriter, status int, value any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if value != nil {
		_ = json.NewEncoder(w).Encode(value)
	}
}

func writeError(w http.ResponseWriter, err error) {
	var invalid *model.ValidationError
	switch {
	case errors.As(err, &invalid):
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": err.Error(), "field": invalid.Field})
	case errors.Is(err, service.ErrNotFound):
		writeJSON(w, http.StatusNotFound, map[string]string{"error": err.Error()})
	case errors.Is(err, service.ErrConflict):
		writeJSON(w, http.StatusConflict, map[string]string{"error": err.Error()})
	default:
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}
}

func decode(r *http.Request, into any) error {
	dec := json.NewDecoder(r.Body)
	dec.DisallowUnknownFields()
	if err := dec.Decode(into); err != nil {
		return &model.ValidationError{Field: "body", Message: err.Error()}
	}
	return nil
}

func pathID(r *http.Request) (int, error) {
	id, err := strconv.Atoi(r.PathValue("id"))
	if err != nil || id < 1 {
		return 0, &model.ValidationError{Field: "id", Message: "must be a positive whole number"}
	}
	return id, nil
}

func queryInt(r *http.Request, name string) (int, bool, error) {
	raw := r.URL.Query().Get(name)
	if raw == "" {
		return 0, false, nil
	}
	v, err := strconv.Atoi(raw)
	if err != nil {
		return 0, false, &model.ValidationError{Field: name, Message: "must be a whole number"}
	}
	return v, true, nil
}

func queryFloat(r *http.Request, name string) (float64, bool, error) {
	raw := r.URL.Query().Get(name)
	if raw == "" {
		return 0, false, nil
	}
	v, err := strconv.ParseFloat(raw, 64)
	if err != nil {
		return 0, false, &model.ValidationError{Field: name, Message: "must be a number"}
	}
	return v, true, nil
}

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

func (a *API) createSupplier(w http.ResponseWriter, r *http.Request) {
	var item model.Supplier
	if err := decode(r, &item); err != nil {
		writeError(w, err)
		return
	}
	created, err := a.svc.CreateSupplier(item)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, created)
}

func (a *API) statsSupplier(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, a.svc.SupplierStats())
}

func (a *API) getSupplier(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.GetSupplier(id)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) updateSupplier(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	var patch model.SupplierPatch
	if err := decode(r, &patch); err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.UpdateSupplier(id, patch)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) deleteSupplier(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	if err := a.svc.DeleteSupplier(id); err != nil {
		writeError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

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

func (a *API) createProduct(w http.ResponseWriter, r *http.Request) {
	var item model.Product
	if err := decode(r, &item); err != nil {
		writeError(w, err)
		return
	}
	created, err := a.svc.CreateProduct(item)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, created)
}

func (a *API) statsProduct(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, a.svc.ProductStats())
}

func (a *API) getProduct(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.GetProduct(id)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) updateProduct(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	var patch model.ProductPatch
	if err := decode(r, &patch); err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.UpdateProduct(id, patch)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) deleteProduct(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	if err := a.svc.DeleteProduct(id); err != nil {
		writeError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

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

func (a *API) createBin(w http.ResponseWriter, r *http.Request) {
	var item model.Bin
	if err := decode(r, &item); err != nil {
		writeError(w, err)
		return
	}
	created, err := a.svc.CreateBin(item)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, created)
}

func (a *API) statsBin(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, a.svc.BinStats())
}

func (a *API) getBin(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.GetBin(id)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) updateBin(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	var patch model.BinPatch
	if err := decode(r, &patch); err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.UpdateBin(id, patch)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) deleteBin(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	if err := a.svc.DeleteBin(id); err != nil {
		writeError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

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

func (a *API) createStockMovement(w http.ResponseWriter, r *http.Request) {
	var item model.StockMovement
	if err := decode(r, &item); err != nil {
		writeError(w, err)
		return
	}
	created, err := a.svc.CreateStockMovement(item)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, created)
}

func (a *API) statsStockMovement(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, a.svc.StockMovementStats())
}

func (a *API) getStockMovement(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.GetStockMovement(id)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) updateStockMovement(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	var patch model.StockMovementPatch
	if err := decode(r, &patch); err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.UpdateStockMovement(id, patch)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) deleteStockMovement(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	if err := a.svc.DeleteStockMovement(id); err != nil {
		writeError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

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

func (a *API) createPurchaseOrder(w http.ResponseWriter, r *http.Request) {
	var item model.PurchaseOrder
	if err := decode(r, &item); err != nil {
		writeError(w, err)
		return
	}
	created, err := a.svc.CreatePurchaseOrder(item)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, created)
}

func (a *API) statsPurchaseOrder(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, a.svc.PurchaseOrderStats())
}

func (a *API) getPurchaseOrder(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.GetPurchaseOrder(id)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) updatePurchaseOrder(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	var patch model.PurchaseOrderPatch
	if err := decode(r, &patch); err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.UpdatePurchaseOrder(id, patch)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) deletePurchaseOrder(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	if err := a.svc.DeletePurchaseOrder(id); err != nil {
		writeError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

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

func (a *API) createStockCount(w http.ResponseWriter, r *http.Request) {
	var item model.StockCount
	if err := decode(r, &item); err != nil {
		writeError(w, err)
		return
	}
	created, err := a.svc.CreateStockCount(item)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, created)
}

func (a *API) statsStockCount(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, a.svc.StockCountStats())
}

func (a *API) getStockCount(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.GetStockCount(id)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) updateStockCount(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	var patch model.StockCountPatch
	if err := decode(r, &patch); err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.UpdateStockCount(id, patch)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) deleteStockCount(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	if err := a.svc.DeleteStockCount(id); err != nil {
		writeError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

func (a *API) listDocuments(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListDocuments()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.Documents.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.Document) bool { return hits[item.ID] })
	}
	if id, ok, err := queryInt(r, "supplier_id"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Document) bool { return item.SupplierID == id })
	}
	if value := q.Get("title"); value != "" {
		items = keep(items, func(item model.Document) bool { return item.Title == value })
	}
	if limit, ok, err := queryInt(r, "min_pages"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Document) bool { return item.Pages >= limit })
	}
	if limit, ok, err := queryInt(r, "max_pages"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Document) bool { return item.Pages <= limit })
	}
	if flag, ok, err := queryBool(r, "signed"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Document) bool { return item.Signed == flag })
	}
	if limit, ok, err := queryInt(r, "min_version"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Document) bool { return item.Version >= limit })
	}
	if limit, ok, err := queryInt(r, "max_version"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Document) bool { return item.Version <= limit })
	}
	if day := q.Get("issued_from"); day != "" {
		items = keep(items, func(item model.Document) bool { return item.Issued >= day })
	}
	if day := q.Get("issued_to"); day != "" {
		items = keep(items, func(item model.Document) bool { return item.Issued <= day })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}

func (a *API) createDocument(w http.ResponseWriter, r *http.Request) {
	var item model.Document
	if err := decode(r, &item); err != nil {
		writeError(w, err)
		return
	}
	created, err := a.svc.CreateDocument(item)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, created)
}

func (a *API) statsDocument(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, a.svc.DocumentStats())
}

func (a *API) getDocument(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.GetDocument(id)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) updateDocument(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	var patch model.DocumentPatch
	if err := decode(r, &patch); err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.UpdateDocument(id, patch)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) deleteDocument(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	if err := a.svc.DeleteDocument(id); err != nil {
		writeError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

func (a *API) listNotifications(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListNotifications()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.Notifications.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.Notification) bool { return hits[item.ID] })
	}
	if value := q.Get("recipient"); value != "" {
		items = keep(items, func(item model.Notification) bool { return item.Recipient == value })
	}
	if value := q.Get("title"); value != "" {
		items = keep(items, func(item model.Notification) bool { return item.Title == value })
	}
	if day := q.Get("sent_from"); day != "" {
		items = keep(items, func(item model.Notification) bool { return item.Sent >= day })
	}
	if day := q.Get("sent_to"); day != "" {
		items = keep(items, func(item model.Notification) bool { return item.Sent <= day })
	}
	if raw := q.Get("channel"); raw != "" {
		wanted, err := model.ParseNotificationChannel(raw)
		if err != nil {
			writeError(w, err)
			return
		}
		items = keep(items, func(item model.Notification) bool { return item.Channel == wanted })
	}
	if flag, ok, err := queryBool(r, "read"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Notification) bool { return item.Read == flag })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}

func (a *API) createNotification(w http.ResponseWriter, r *http.Request) {
	var item model.Notification
	if err := decode(r, &item); err != nil {
		writeError(w, err)
		return
	}
	created, err := a.svc.CreateNotification(item)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, created)
}

func (a *API) statsNotification(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, a.svc.NotificationStats())
}

func (a *API) getNotification(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.GetNotification(id)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) updateNotification(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	var patch model.NotificationPatch
	if err := decode(r, &patch); err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.UpdateNotification(id, patch)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) deleteNotification(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	if err := a.svc.DeleteNotification(id); err != nil {
		writeError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
