package httpapi

import (
	"net/http"

	"library-api/internal/model"
)

func (a *API) listBooks(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListBooks()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.Books.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.Book) bool { return hits[item.ID] })
	}
	if value := q.Get("title"); value != "" {
		items = keep(items, func(item model.Book) bool { return item.Title == value })
	}
	if id, ok, err := queryInt(r, "author_id"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Book) bool { return item.AuthorID == id })
	}
	if value := q.Get("isbn"); value != "" {
		items = keep(items, func(item model.Book) bool { return item.Isbn == value })
	}
	if limit, ok, err := queryInt(r, "min_pages"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Book) bool { return item.Pages >= limit })
	}
	if limit, ok, err := queryInt(r, "max_pages"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Book) bool { return item.Pages <= limit })
	}
	if limit, ok, err := queryFloat(r, "min_price"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Book) bool { return item.Price >= limit })
	}
	if limit, ok, err := queryFloat(r, "max_price"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Book) bool { return item.Price <= limit })
	}
	if day := q.Get("published_from"); day != "" {
		items = keep(items, func(item model.Book) bool { return item.Published >= day })
	}
	if day := q.Get("published_to"); day != "" {
		items = keep(items, func(item model.Book) bool { return item.Published <= day })
	}
	if raw := q.Get("genre"); raw != "" {
		wanted, err := model.ParseBookGenre(raw)
		if err != nil {
			writeError(w, err)
			return
		}
		items = keep(items, func(item model.Book) bool { return item.Genre == wanted })
	}
	if flag, ok, err := queryBool(r, "available"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Book) bool { return item.Available == flag })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}
