package httpapi

import (
	"net/http"

	"fleet-api/internal/model"
)

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
