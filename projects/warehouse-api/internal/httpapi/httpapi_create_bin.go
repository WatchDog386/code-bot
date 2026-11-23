package httpapi

import (
	"net/http"

	"warehouse-api/internal/model"
)

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
