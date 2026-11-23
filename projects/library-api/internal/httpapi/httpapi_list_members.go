package httpapi

import (
	"net/http"

	"library-api/internal/model"
)

func (a *API) listMembers(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListMembers()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.Members.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.Member) bool { return hits[item.ID] })
	}
	if value := q.Get("name"); value != "" {
		items = keep(items, func(item model.Member) bool { return item.Name == value })
	}
	if value := q.Get("email"); value != "" {
		items = keep(items, func(item model.Member) bool { return item.Email == value })
	}
	if value := q.Get("phone"); value != "" {
		items = keep(items, func(item model.Member) bool { return item.Phone == value })
	}
	if day := q.Get("joined_from"); day != "" {
		items = keep(items, func(item model.Member) bool { return item.Joined >= day })
	}
	if day := q.Get("joined_to"); day != "" {
		items = keep(items, func(item model.Member) bool { return item.Joined <= day })
	}
	if raw := q.Get("tier"); raw != "" {
		wanted, err := model.ParseMemberTier(raw)
		if err != nil {
			writeError(w, err)
			return
		}
		items = keep(items, func(item model.Member) bool { return item.Tier == wanted })
	}
	if limit, ok, err := queryFloat(r, "min_fines"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Member) bool { return item.Fines >= limit })
	}
	if limit, ok, err := queryFloat(r, "max_fines"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Member) bool { return item.Fines <= limit })
	}
	if flag, ok, err := queryBool(r, "active"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Member) bool { return item.Active == flag })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}
