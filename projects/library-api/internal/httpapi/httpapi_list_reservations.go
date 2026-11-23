package httpapi

import (
	"net/http"

	"library-api/internal/model"
)

func (a *API) listReservations(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListReservations()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.Reservations.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.Reservation) bool { return hits[item.ID] })
	}
	if id, ok, err := queryInt(r, "book_id"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Reservation) bool { return item.BookID == id })
	}
	if id, ok, err := queryInt(r, "member_id"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Reservation) bool { return item.MemberID == id })
	}
	if day := q.Get("requested_from"); day != "" {
		items = keep(items, func(item model.Reservation) bool { return item.Requested >= day })
	}
	if day := q.Get("requested_to"); day != "" {
		items = keep(items, func(item model.Reservation) bool { return item.Requested <= day })
	}
	if limit, ok, err := queryInt(r, "min_position"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Reservation) bool { return item.Position >= limit })
	}
	if limit, ok, err := queryInt(r, "max_position"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Reservation) bool { return item.Position <= limit })
	}
	if raw := q.Get("status"); raw != "" {
		wanted, err := model.ParseReservationStatus(raw)
		if err != nil {
			writeError(w, err)
			return
		}
		items = keep(items, func(item model.Reservation) bool { return item.Status == wanted })
	}
	if value := q.Get("notes"); value != "" {
		items = keep(items, func(item model.Reservation) bool { return item.Notes == value })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}
