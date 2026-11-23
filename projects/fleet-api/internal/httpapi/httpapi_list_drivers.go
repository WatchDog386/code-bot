package httpapi

import (
	"net/http"

	"fleet-api/internal/model"
)

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
