package httpapi

import (
	"net/http"

	"warehouse-api/internal/model"
)

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
