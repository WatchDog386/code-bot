// Package httpapi serves the Warehouse Inventory service as JSON over HTTP (net/http only).
//
// Every collection has GET (list, with filters, ?q= search, ?page=&size=), POST,
// GET /{id}, PATCH /{id}, DELETE /{id} and GET /stats.
package httpapi

import (
	"encoding/json"
	"errors"
	"net/http"

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
