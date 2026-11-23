package httpapi

import (
	"net/http"

	"warehouse-api/internal/model"
)

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
