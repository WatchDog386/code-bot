package httpapi

import (
	"net/http"

	"library-api/internal/model"
)

func (a *API) listLoans(w http.ResponseWriter, r *http.Request) {
	items := a.svc.ListLoans()
	q := r.URL.Query()
	if text := q.Get("q"); text != "" {
		hits := map[int]bool{}
		for _, item := range a.svc.Loans.Search(text) {
			hits[item.ID] = true
		}
		items = keep(items, func(item model.Loan) bool { return hits[item.ID] })
	}
	if id, ok, err := queryInt(r, "book_id"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Loan) bool { return item.BookID == id })
	}
	if id, ok, err := queryInt(r, "member_id"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Loan) bool { return item.MemberID == id })
	}
	if day := q.Get("borrowed_from"); day != "" {
		items = keep(items, func(item model.Loan) bool { return item.Borrowed >= day })
	}
	if day := q.Get("borrowed_to"); day != "" {
		items = keep(items, func(item model.Loan) bool { return item.Borrowed <= day })
	}
	if day := q.Get("due_from"); day != "" {
		items = keep(items, func(item model.Loan) bool { return item.Due >= day })
	}
	if day := q.Get("due_to"); day != "" {
		items = keep(items, func(item model.Loan) bool { return item.Due <= day })
	}
	if limit, ok, err := queryInt(r, "min_renewals"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Loan) bool { return item.Renewals >= limit })
	}
	if limit, ok, err := queryInt(r, "max_renewals"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Loan) bool { return item.Renewals <= limit })
	}
	if raw := q.Get("status"); raw != "" {
		wanted, err := model.ParseLoanStatus(raw)
		if err != nil {
			writeError(w, err)
			return
		}
		items = keep(items, func(item model.Loan) bool { return item.Status == wanted })
	}
	if limit, ok, err := queryFloat(r, "min_fee"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Loan) bool { return item.Fee >= limit })
	}
	if limit, ok, err := queryFloat(r, "max_fee"); err != nil {
		writeError(w, err)
		return
	} else if ok {
		items = keep(items, func(item model.Loan) bool { return item.Fee <= limit })
	}
	page, err := window(r, items)
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, page)
}
