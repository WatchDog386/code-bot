package httpapi

import (
	"net/http"

	"library-api/internal/model"
)

func (a *API) createLoan(w http.ResponseWriter, r *http.Request) {
	var item model.Loan
	if err := decode(r, &item); err != nil {
		writeError(w, err)
		return
	}
	created, err := a.svc.CreateLoan(item)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, created)
}

func (a *API) statsLoan(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, a.svc.LoanStats())
}

func (a *API) getLoan(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.GetLoan(id)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}
