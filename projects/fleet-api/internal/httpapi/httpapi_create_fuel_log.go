package httpapi

import (
	"net/http"

	"fleet-api/internal/model"
)

func (a *API) createFuelLog(w http.ResponseWriter, r *http.Request) {
	var item model.FuelLog
	if err := decode(r, &item); err != nil {
		writeError(w, err)
		return
	}
	created, err := a.svc.CreateFuelLog(item)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, created)
}

func (a *API) statsFuelLog(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, a.svc.FuelLogStats())
}

func (a *API) getFuelLog(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.GetFuelLog(id)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}
