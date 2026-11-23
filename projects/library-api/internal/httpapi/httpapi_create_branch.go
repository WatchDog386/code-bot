package httpapi

import (
	"net/http"

	"library-api/internal/model"
)

func (a *API) createBranch(w http.ResponseWriter, r *http.Request) {
	var item model.Branch
	if err := decode(r, &item); err != nil {
		writeError(w, err)
		return
	}
	created, err := a.svc.CreateBranch(item)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, created)
}

func (a *API) statsBranch(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, a.svc.BranchStats())
}

func (a *API) getBranch(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		writeError(w, err)
		return
	}
	item, err := a.svc.GetBranch(id)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, item)
}
