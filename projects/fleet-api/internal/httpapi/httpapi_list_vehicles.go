package httpapi

import (
	"net/http"

	"fleet-api/internal/model"
)

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
