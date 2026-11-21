// Package httpapi serves the Fleet Management service as JSON over HTTP (net/http only).
//
// Every collection has GET (list, with filters, ?q= search, ?page=&size=), POST,
// GET /{id}, PATCH /{id}, DELETE /{id} and GET /stats.
package httpapi

import (
	"encoding/json"
	"errors"
	"net/http"
	"strconv"

	"fleet-api/internal/model"
	"fleet-api/internal/service"
)

// API answers HTTP requests using the service.
type API struct {
	svc *service.Service
}

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
	mux.HandleFunc("GET /documents", a.listDocuments)
	mux.HandleFunc("POST /documents", a.createDocument)
	mux.HandleFunc("GET /documents/stats", a.statsDocument)
	mux.HandleFunc("GET /documents/{id}", a.getDocument)
	mux.HandleFunc("PATCH /documents/{id}", a.updateDocument)
	mux.HandleFunc("DELETE /documents/{id}", a.deleteDocument)
	mux.HandleFunc("GET /notifications", a.listNotifications)
	mux.HandleFunc("POST /notifications", a.createNotification)
	mux.HandleFunc("GET /notifications/stats", a.statsNotification)
	mux.HandleFunc("GET /notifications/{id}", a.getNotification)
	mux.HandleFunc("PATCH /notifications/{id}", a.updateNotification)
	mux.HandleFunc("DELETE /notifications/{id}", a.deleteNotification)
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

func pathID(r *http.Request) (int, error) {
	id, err := strconv.Atoi(r.PathValue("id"))
	if err != nil || id < 1 {
		return 0, &model.ValidationError{Field: "id", Message: "must be a positive whole number"}
	}
	return id, nil
}

func queryInt(r *http.Request, name string) (int, bool, error) {
	raw := r.URL.Query().Get(name)
	if raw == "" {
		return 0, false, nil
	}
	v, err := strconv.Atoi(raw)
	if err != nil {
		return 0, false, &model.ValidationError{Field: name, Message: "must be a whole number"}
	}
	return v, true, nil
}

func queryFloat(r *http.Request, name string) (float64, bool, error) {
	raw := r.URL.Query().Get(name)
	if raw == "" {
		return 0, false, nil
	}
	v, err := strconv.ParseFloat(raw, 64)
	if err != nil {
		return 0, false, &model.ValidationError{Field: name, Message: "must be a number"}
	}
	return v, true, nil
}

func queryBool(r *http.Request, name string) (bool, bool, error) {
	raw := r.URL.Query().Get(name)
	if raw == "" {
		return false, false, nil
	}
	v, err := strconv.ParseBool(raw)
	if err != nil {
		return false, false, &model.ValidationError{Field: name, Message: "must be true or false"}
	}
	return v, true, nil
}

// keep returns the items ok() accepts.
func keep[T any](items []T, ok func(T) bool) []T {
	out := make([]T, 0, len(items))
	for _, item := range items {
		if ok(item) {
			out = append(out, item)
		}
	}
	return out
}

// window returns one page of items (?page= from 1, ?size= up to 200).
func window[T any](r *http.Request, items []T) ([]T, error) {
	page, ok, err := queryInt(r, "page")
	if err != nil {
		return nil, err
	}
	if !ok || page < 1 {
		page = 1
	}
	size, ok, err := queryInt(r, "size")
	if err != nil {
		return nil, err
	}
	if !ok || size < 1 || size > 200 {
		size = 50
	}
	start := (page - 1) * size
	if start >= len(items) {
		return []T{}, nil
	}
	end := min(start+size, len(items))
	return items[start:end], nil
}

func (a *API) listVehicles(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListVehicles()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.Vehicles.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.Vehicle) bool { return hits[item.ID] })
	}
	if value := q.Get("plate"); value != "" {
		items = keep(items, func(item model.Vehicle) bool { return item.Plate == value })
	}
	if value := q.Get("make"); value != "" {
		items = keep(items, func(item model.Vehicle) bool { return item.Make == value })
	}
	if value := q.Get("model"); value != "" {
		items = keep(items, func(item model.Vehicle) bool { return item.Model == value })
	}
	if limit, ok, err := queryInt(r, "min_year"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Vehicle) bool { return item.Year >= limit })
	}
	if limit, ok, err := queryInt(r, "max_year"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Vehicle) bool { return item.Year <= limit })
	}
	if limit, ok, err := queryInt(r, "min_mileage"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Vehicle) bool { return item.Mileage >= limit })
	}
	if limit, ok, err := queryInt(r, "max_mileage"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Vehicle) bool { return item.Mileage <= limit })
	}
	if raw := q.Get("fuel"); raw != "" {
		wanted, err := model.ParseVehicleFuel(raw)
		if err != nil {
			writeError(w, err)
			return
		}
		items = keep(items, func(item model.Vehicle) bool { return item.Fuel == wanted })
	}
	if flag, ok, err := queryBool(r, "active"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Vehicle) bool { return item.Active == flag })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}

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

func (a *API) updateVehicle(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	var patch model.VehiclePatch
	if err := decode(r, &patch); err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.UpdateVehicle(id, patch)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) deleteVehicle(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	if err := a.svc.DeleteVehicle(id); err != nil {
		writeError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

func (a *API) listDrivers(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListDrivers()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.Drivers.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.Driver) bool { return hits[item.ID] })
	}
	if value := q.Get("name"); value != "" {
		items = keep(items, func(item model.Driver) bool { return item.Name == value })
	}
	if value := q.Get("email"); value != "" {
		items = keep(items, func(item model.Driver) bool { return item.Email == value })
	}
	if value := q.Get("license_no"); value != "" {
		items = keep(items, func(item model.Driver) bool { return item.LicenseNo == value })
	}
	if day := q.Get("license_expiry_from"); day != "" {
		items = keep(items, func(item model.Driver) bool { return item.LicenseExpiry >= day })
	}
	if day := q.Get("license_expiry_to"); day != "" {
		items = keep(items, func(item model.Driver) bool { return item.LicenseExpiry <= day })
	}
	if limit, ok, err := queryFloat(r, "min_rating"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Driver) bool { return item.Rating >= limit })
	}
	if limit, ok, err := queryFloat(r, "max_rating"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Driver) bool { return item.Rating <= limit })
	}
	if flag, ok, err := queryBool(r, "on_duty"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Driver) bool { return item.OnDuty == flag })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}

func (a *API) createDriver(w http.ResponseWriter, r *http.Request) {
	var item model.Driver
	if err := decode(r, &item); err != nil {
		writeError(w, err)
		return
	}
	created, err := a.svc.CreateDriver(item)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, created)
}

func (a *API) statsDriver(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, a.svc.DriverStats())
}

func (a *API) getDriver(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.GetDriver(id)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) updateDriver(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	var patch model.DriverPatch
	if err := decode(r, &patch); err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.UpdateDriver(id, patch)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) deleteDriver(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	if err := a.svc.DeleteDriver(id); err != nil {
		writeError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

func (a *API) listTrips(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListTrips()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.Trips.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.Trip) bool { return hits[item.ID] })
	}
	if id, ok, err := queryInt(r, "vehicle_id"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Trip) bool { return item.VehicleID == id })
	}
	if id, ok, err := queryInt(r, "driver_id"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Trip) bool { return item.DriverID == id })
	}
	if day := q.Get("started_from"); day != "" {
		items = keep(items, func(item model.Trip) bool { return item.Started >= day })
	}
	if day := q.Get("started_to"); day != "" {
		items = keep(items, func(item model.Trip) bool { return item.Started <= day })
	}
	if limit, ok, err := queryFloat(r, "min_distance_km"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Trip) bool { return item.DistanceKm >= limit })
	}
	if limit, ok, err := queryFloat(r, "max_distance_km"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Trip) bool { return item.DistanceKm <= limit })
	}
	if value := q.Get("purpose"); value != "" {
		items = keep(items, func(item model.Trip) bool { return item.Purpose == value })
	}
	if raw := q.Get("status"); raw != "" {
		wanted, err := model.ParseTripStatus(raw)
		if err != nil {
			writeError(w, err)
			return
		}
		items = keep(items, func(item model.Trip) bool { return item.Status == wanted })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}

func (a *API) createTrip(w http.ResponseWriter, r *http.Request) {
	var item model.Trip
	if err := decode(r, &item); err != nil {
		writeError(w, err)
		return
	}
	created, err := a.svc.CreateTrip(item)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, created)
}

func (a *API) statsTrip(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, a.svc.TripStats())
}

func (a *API) getTrip(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.GetTrip(id)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) updateTrip(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	var patch model.TripPatch
	if err := decode(r, &patch); err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.UpdateTrip(id, patch)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) deleteTrip(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	if err := a.svc.DeleteTrip(id); err != nil {
		writeError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

func (a *API) listFuelLogs(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListFuelLogs()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.FuelLogs.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.FuelLog) bool { return hits[item.ID] })
	}
	if id, ok, err := queryInt(r, "vehicle_id"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.FuelLog) bool { return item.VehicleID == id })
	}
	if day := q.Get("filled_from"); day != "" {
		items = keep(items, func(item model.FuelLog) bool { return item.Filled >= day })
	}
	if day := q.Get("filled_to"); day != "" {
		items = keep(items, func(item model.FuelLog) bool { return item.Filled <= day })
	}
	if limit, ok, err := queryFloat(r, "min_litres"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.FuelLog) bool { return item.Litres >= limit })
	}
	if limit, ok, err := queryFloat(r, "max_litres"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.FuelLog) bool { return item.Litres <= limit })
	}
	if limit, ok, err := queryFloat(r, "min_cost"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.FuelLog) bool { return item.Cost >= limit })
	}
	if limit, ok, err := queryFloat(r, "max_cost"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.FuelLog) bool { return item.Cost <= limit })
	}
	if value := q.Get("station"); value != "" {
		items = keep(items, func(item model.FuelLog) bool { return item.Station == value })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}

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

func (a *API) updateFuelLog(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	var patch model.FuelLogPatch
	if err := decode(r, &patch); err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.UpdateFuelLog(id, patch)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) deleteFuelLog(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	if err := a.svc.DeleteFuelLog(id); err != nil {
		writeError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

func (a *API) listServiceRecords(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListServiceRecords()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.ServiceRecords.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.ServiceRecord) bool { return hits[item.ID] })
	}
	if id, ok, err := queryInt(r, "vehicle_id"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.ServiceRecord) bool { return item.VehicleID == id })
	}
	if day := q.Get("serviced_from"); day != "" {
		items = keep(items, func(item model.ServiceRecord) bool { return item.Serviced >= day })
	}
	if day := q.Get("serviced_to"); day != "" {
		items = keep(items, func(item model.ServiceRecord) bool { return item.Serviced <= day })
	}
	if limit, ok, err := queryInt(r, "min_odometer"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.ServiceRecord) bool { return item.Odometer >= limit })
	}
	if limit, ok, err := queryInt(r, "max_odometer"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.ServiceRecord) bool { return item.Odometer <= limit })
	}
	if limit, ok, err := queryFloat(r, "min_cost"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.ServiceRecord) bool { return item.Cost >= limit })
	}
	if limit, ok, err := queryFloat(r, "max_cost"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.ServiceRecord) bool { return item.Cost <= limit })
	}
	if raw := q.Get("kind"); raw != "" {
		wanted, err := model.ParseServiceRecordKind(raw)
		if err != nil {
			writeError(w, err)
			return
		}
		items = keep(items, func(item model.ServiceRecord) bool { return item.Kind == wanted })
	}
	if value := q.Get("notes"); value != "" {
		items = keep(items, func(item model.ServiceRecord) bool { return item.Notes == value })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}

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

func (a *API) listIncidents(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListIncidents()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.Incidents.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.Incident) bool { return hits[item.ID] })
	}
	if id, ok, err := queryInt(r, "vehicle_id"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Incident) bool { return item.VehicleID == id })
	}
	if id, ok, err := queryInt(r, "driver_id"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Incident) bool { return item.DriverID == id })
	}
	if day := q.Get("happened_from"); day != "" {
		items = keep(items, func(item model.Incident) bool { return item.Happened >= day })
	}
	if day := q.Get("happened_to"); day != "" {
		items = keep(items, func(item model.Incident) bool { return item.Happened <= day })
	}
	if raw := q.Get("severity"); raw != "" {
		wanted, err := model.ParseIncidentSeverity(raw)
		if err != nil {
			writeError(w, err)
			return
		}
		items = keep(items, func(item model.Incident) bool { return item.Severity == wanted })
	}
	if limit, ok, err := queryFloat(r, "min_damage_cost"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Incident) bool { return item.DamageCost >= limit })
	}
	if limit, ok, err := queryFloat(r, "max_damage_cost"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Incident) bool { return item.DamageCost <= limit })
	}
	if flag, ok, err := queryBool(r, "reported"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Incident) bool { return item.Reported == flag })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}

func (a *API) createIncident(w http.ResponseWriter, r *http.Request) {
	var item model.Incident
	if err := decode(r, &item); err != nil {
		writeError(w, err)
		return
	}
	created, err := a.svc.CreateIncident(item)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, created)
}

func (a *API) statsIncident(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, a.svc.IncidentStats())
}

func (a *API) getIncident(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.GetIncident(id)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) updateIncident(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	var patch model.IncidentPatch
	if err := decode(r, &patch); err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.UpdateIncident(id, patch)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) deleteIncident(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	if err := a.svc.DeleteIncident(id); err != nil {
		writeError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

func (a *API) listDocuments(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListDocuments()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.Documents.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.Document) bool { return hits[item.ID] })
	}
	if id, ok, err := queryInt(r, "vehicle_id"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Document) bool { return item.VehicleID == id })
	}
	if value := q.Get("title"); value != "" {
		items = keep(items, func(item model.Document) bool { return item.Title == value })
	}
	if limit, ok, err := queryInt(r, "min_pages"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Document) bool { return item.Pages >= limit })
	}
	if limit, ok, err := queryInt(r, "max_pages"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Document) bool { return item.Pages <= limit })
	}
	if flag, ok, err := queryBool(r, "signed"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Document) bool { return item.Signed == flag })
	}
	if limit, ok, err := queryInt(r, "min_version"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Document) bool { return item.Version >= limit })
	}
	if limit, ok, err := queryInt(r, "max_version"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Document) bool { return item.Version <= limit })
	}
	if day := q.Get("issued_from"); day != "" {
		items = keep(items, func(item model.Document) bool { return item.Issued >= day })
	}
	if day := q.Get("issued_to"); day != "" {
		items = keep(items, func(item model.Document) bool { return item.Issued <= day })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}

func (a *API) createDocument(w http.ResponseWriter, r *http.Request) {
	var item model.Document
	if err := decode(r, &item); err != nil {
		writeError(w, err)
		return
	}
	created, err := a.svc.CreateDocument(item)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, created)
}

func (a *API) statsDocument(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, a.svc.DocumentStats())
}

func (a *API) getDocument(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.GetDocument(id)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) updateDocument(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	var patch model.DocumentPatch
	if err := decode(r, &patch); err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.UpdateDocument(id, patch)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) deleteDocument(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	if err := a.svc.DeleteDocument(id); err != nil {
		writeError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

func (a *API) listNotifications(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListNotifications()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.Notifications.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.Notification) bool { return hits[item.ID] })
	}
	if value := q.Get("recipient"); value != "" {
		items = keep(items, func(item model.Notification) bool { return item.Recipient == value })
	}
	if value := q.Get("title"); value != "" {
		items = keep(items, func(item model.Notification) bool { return item.Title == value })
	}
	if day := q.Get("sent_from"); day != "" {
		items = keep(items, func(item model.Notification) bool { return item.Sent >= day })
	}
	if day := q.Get("sent_to"); day != "" {
		items = keep(items, func(item model.Notification) bool { return item.Sent <= day })
	}
	if raw := q.Get("channel"); raw != "" {
		wanted, err := model.ParseNotificationChannel(raw)
		if err != nil {
			writeError(w, err)
			return
		}
		items = keep(items, func(item model.Notification) bool { return item.Channel == wanted })
	}
	if flag, ok, err := queryBool(r, "read"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Notification) bool { return item.Read == flag })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}

func (a *API) createNotification(w http.ResponseWriter, r *http.Request) {
	var item model.Notification
	if err := decode(r, &item); err != nil {
		writeError(w, err)
		return
	}
	created, err := a.svc.CreateNotification(item)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, created)
}

func (a *API) statsNotification(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, a.svc.NotificationStats())
}

func (a *API) getNotification(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.GetNotification(id)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) updateNotification(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	var patch model.NotificationPatch
	if err := decode(r, &patch); err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.UpdateNotification(id, patch)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}

func (a *API) deleteNotification(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	if err := a.svc.DeleteNotification(id); err != nil {
		writeError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
