package httpapi

import (
	"net/http"

	"fleet-api/internal/model"
)

func (a *API) createServiceRecord(w http.ResponseWriter, r *http.Request) {
	var item model.ServiceRecord
	if err := decode(r, &item); err != nil {
		writeError(w, err)
		return
	}
	created, err := a.svc.CreateServiceRecord(item)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, created)
}

func (a *API) statsServiceRecord(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, a.svc.ServiceRecordStats())
}

func (a *API) getServiceRecord(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.GetServiceRecord(id)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}
