package httpapi

import (
	"net/http"

	"warehouse-api/internal/model"
)

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
