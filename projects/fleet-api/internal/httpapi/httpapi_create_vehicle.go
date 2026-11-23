package httpapi

import (
	"net/http"

	"fleet-api/internal/model"
)

func (a *API) createVehicle(w http.ResponseWriter, r *http.Request) {
	var item model.Vehicle
	if err := decode(r, &item); err != nil {
		writeError(w, err)
		return
	}
	created, err := a.svc.CreateVehicle(item)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, created)
}

func (a *API) statsVehicle(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, a.svc.VehicleStats())
}

func (a *API) getVehicle(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.GetVehicle(id)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}
