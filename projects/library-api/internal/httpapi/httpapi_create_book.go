package httpapi

import (
	"net/http"

	"library-api/internal/model"
)

func (a *API) createBook(w http.ResponseWriter, r *http.Request) {
	var item model.Book
	if err := decode(r, &item); err != nil {
		writeError(w, err)
		return
	}
	created, err := a.svc.CreateBook(item)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, created)
}

func (a *API) statsBook(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, a.svc.BookStats())
}

func (a *API) getBook(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.GetBook(id)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}
