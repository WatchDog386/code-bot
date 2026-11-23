package httpapi

import (
	"net/http"

	"library-api/internal/model"
)

func (a *API) listAuthors(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListAuthors()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.Authors.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.Author) bool { return hits[item.ID] })
	}
	if value := q.Get("name"); value != "" {
		items = keep(items, func(item model.Author) bool { return item.Name == value })
	}
	if value := q.Get("email"); value != "" {
		items = keep(items, func(item model.Author) bool { return item.Email == value })
	}
	if value := q.Get("country"); value != "" {
		items = keep(items, func(item model.Author) bool { return item.Country == value })
	}
	if day := q.Get("born_from"); day != "" {
		items = keep(items, func(item model.Author) bool { return item.Born >= day })
	}
	if day := q.Get("born_to"); day != "" {
		items = keep(items, func(item model.Author) bool { return item.Born <= day })
	}
	if flag, ok, err := queryBool(r, "active"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Author) bool { return item.Active == flag })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}
