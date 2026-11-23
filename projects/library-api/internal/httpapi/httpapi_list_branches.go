package httpapi

import (
	"net/http"

	"library-api/internal/model"
)

func (a *API) listBranches(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListBranches()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.Branches.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.Branch) bool { return hits[item.ID] })
	}
	if value := q.Get("name"); value != "" {
		items = keep(items, func(item model.Branch) bool { return item.Name == value })
	}
	if value := q.Get("city"); value != "" {
		items = keep(items, func(item model.Branch) bool { return item.City == value })
	}
	if value := q.Get("phone"); value != "" {
		items = keep(items, func(item model.Branch) bool { return item.Phone == value })
	}
	if day := q.Get("opened_from"); day != "" {
		items = keep(items, func(item model.Branch) bool { return item.Opened >= day })
	}
	if day := q.Get("opened_to"); day != "" {
		items = keep(items, func(item model.Branch) bool { return item.Opened <= day })
	}
	if limit, ok, err := queryInt(r, "min_seats"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Branch) bool { return item.Seats >= limit })
	}
	if limit, ok, err := queryInt(r, "max_seats"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Branch) bool { return item.Seats <= limit })
	}
	if flag, ok, err := queryBool(r, "open_late"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Branch) bool { return item.OpenLate == flag })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}
