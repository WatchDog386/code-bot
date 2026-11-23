package httpapi

import (
	"net/http"

	"warehouse-api/internal/model"
)

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
