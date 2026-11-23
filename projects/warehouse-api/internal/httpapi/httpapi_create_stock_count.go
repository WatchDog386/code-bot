package httpapi

import (
	"net/http"

	"warehouse-api/internal/model"
)

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
