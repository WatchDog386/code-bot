package httpapi

import (
	"encoding/json"
	"errors"
	"net/http"

	"fleet-api/internal/model"
	"fleet-api/internal/service"
)

// New returns the routes of the whole service.
func New(svc *service.Service) http.Handler {
	a := &API{svc: svc}
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", func(w http.ResponseWriter, _ *http.Request) {
		writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
	})
	mux.HandleFunc("GET /vehicles", a.listVehicles)
	mux.HandleFunc("POST /vehicles", a.createVehicle)
	mux.HandleFunc("GET /vehicles/stats", a.statsVehicle)
	mux.HandleFunc("GET /vehicles/{id}", a.getVehicle)
	mux.HandleFunc("PATCH /vehicles/{id}", a.updateVehicle)
	mux.HandleFunc("DELETE /vehicles/{id}", a.deleteVehicle)
	mux.HandleFunc("GET /drivers", a.listDrivers)
	mux.HandleFunc("POST /drivers", a.createDriver)
	mux.HandleFunc("GET /drivers/stats", a.statsDriver)
	mux.HandleFunc("GET /drivers/{id}", a.getDriver)
	mux.HandleFunc("PATCH /drivers/{id}", a.updateDriver)
	mux.HandleFunc("DELETE /drivers/{id}", a.deleteDriver)
	mux.HandleFunc("GET /trips", a.listTrips)
	mux.HandleFunc("POST /trips", a.createTrip)
	mux.HandleFunc("GET /trips/stats", a.statsTrip)
	mux.HandleFunc("GET /trips/{id}", a.getTrip)
	mux.HandleFunc("PATCH /trips/{id}", a.updateTrip)
	mux.HandleFunc("DELETE /trips/{id}", a.deleteTrip)
	mux.HandleFunc("GET /fuel-logs", a.listFuelLogs)
	mux.HandleFunc("POST /fuel-logs", a.createFuelLog)
	mux.HandleFunc("GET /fuel-logs/stats", a.statsFuelLog)
	mux.HandleFunc("GET /fuel-logs/{id}", a.getFuelLog)
	mux.HandleFunc("PATCH /fuel-logs/{id}", a.updateFuelLog)
	mux.HandleFunc("DELETE /fuel-logs/{id}", a.deleteFuelLog)
	mux.HandleFunc("GET /service-records", a.listServiceRecords)
	mux.HandleFunc("POST /service-records", a.createServiceRecord)
	mux.HandleFunc("GET /service-records/stats", a.statsServiceRecord)
	mux.HandleFunc("GET /service-records/{id}", a.getServiceRecord)
	mux.HandleFunc("PATCH /service-records/{id}", a.updateServiceRecord)
	mux.HandleFunc("DELETE /service-records/{id}", a.deleteServiceRecord)
	mux.HandleFunc("GET /incidents", a.listIncidents)
	mux.HandleFunc("POST /incidents", a.createIncident)
	mux.HandleFunc("GET /incidents/stats", a.statsIncident)
	mux.HandleFunc("GET /incidents/{id}", a.getIncident)
	mux.HandleFunc("PATCH /incidents/{id}", a.updateIncident)
	mux.HandleFunc("DELETE /incidents/{id}", a.deleteIncident)
	return mux
}

func writeJSON(w http.ResponseWriter, status int, value any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if value != nil {
		_ = json.NewEncoder(w).Encode(value)
	}
}

func writeError(w http.ResponseWriter, err error) {
	var invalid *model.ValidationError
	switch {
	case errors.As(err, &invalid):
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": err.Error(), "field": invalid.Field})
	case errors.Is(err, service.ErrNotFound):
		writeJSON(w, http.StatusNotFound, map[string]string{"error": err.Error()})
	case errors.Is(err, service.ErrConflict):
		writeJSON(w, http.StatusConflict, map[string]string{"error": err.Error()})
	default:
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}
}

func decode(r *http.Request, into any) error {
	dec := json.NewDecoder(r.Body)
	dec.DisallowUnknownFields()
	if err := dec.Decode(into); err != nil {
		return &model.ValidationError{Field: "body", Message: err.Error()}
	}
	return nil
}
