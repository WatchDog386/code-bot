package httpapi

import (
	"net/http"

	"fleet-api/internal/model"
)

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
