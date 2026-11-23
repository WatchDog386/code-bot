package httpapi

import (
	"net/http"

	"fleet-api/internal/model"
)

func (a *API) updateServiceRecord(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	var patch model.ServiceRecordPatch
	if err := decode(r, &patch); err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.UpdateServiceRecord(id, patch)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) deleteServiceRecord(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	if err := a.svc.DeleteServiceRecord(id); err != nil {
		writeError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
