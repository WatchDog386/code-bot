package httpapi

import (
	"net/http"

	"fleet-api/internal/model"
)

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
