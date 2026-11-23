package httpapi

import (
	"net/http"

	"fleet-api/internal/model"
)

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
