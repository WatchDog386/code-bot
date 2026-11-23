package httpapi

import (
	"net/http"

	"library-api/internal/service"
)

// New returns the routes of the whole service.
func New(svc *service.Service) http.Handler {
	a := &API{svc: svc}
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", func(w http.ResponseWriter, _ *http.Request) {
		writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
	})
	mux.HandleFunc("GET /authors", a.listAuthors)
	mux.HandleFunc("POST /authors", a.createAuthor)
	mux.HandleFunc("GET /authors/stats", a.statsAuthor)
	mux.HandleFunc("GET /authors/{id}", a.getAuthor)
	mux.HandleFunc("PATCH /authors/{id}", a.updateAuthor)
	mux.HandleFunc("DELETE /authors/{id}", a.deleteAuthor)
	mux.HandleFunc("GET /books", a.listBooks)
	mux.HandleFunc("POST /books", a.createBook)
	mux.HandleFunc("GET /books/stats", a.statsBook)
	mux.HandleFunc("GET /books/{id}", a.getBook)
	mux.HandleFunc("PATCH /books/{id}", a.updateBook)
	mux.HandleFunc("DELETE /books/{id}", a.deleteBook)
	mux.HandleFunc("GET /members", a.listMembers)
	mux.HandleFunc("POST /members", a.createMember)
	mux.HandleFunc("GET /members/stats", a.statsMember)
	mux.HandleFunc("GET /members/{id}", a.getMember)
	mux.HandleFunc("PATCH /members/{id}", a.updateMember)
	mux.HandleFunc("DELETE /members/{id}", a.deleteMember)
	mux.HandleFunc("GET /loans", a.listLoans)
	mux.HandleFunc("POST /loans", a.createLoan)
	mux.HandleFunc("GET /loans/stats", a.statsLoan)
	mux.HandleFunc("GET /loans/{id}", a.getLoan)
	mux.HandleFunc("PATCH /loans/{id}", a.updateLoan)
	mux.HandleFunc("DELETE /loans/{id}", a.deleteLoan)
	mux.HandleFunc("GET /reservations", a.listReservations)
	mux.HandleFunc("POST /reservations", a.createReservation)
	mux.HandleFunc("GET /reservations/stats", a.statsReservation)
	mux.HandleFunc("GET /reservations/{id}", a.getReservation)
	mux.HandleFunc("PATCH /reservations/{id}", a.updateReservation)
	mux.HandleFunc("DELETE /reservations/{id}", a.deleteReservation)
	mux.HandleFunc("GET /branches", a.listBranches)
	mux.HandleFunc("POST /branches", a.createBranch)
	mux.HandleFunc("GET /branches/stats", a.statsBranch)
	mux.HandleFunc("GET /branches/{id}", a.getBranch)
	mux.HandleFunc("PATCH /branches/{id}", a.updateBranch)
	mux.HandleFunc("DELETE /branches/{id}", a.deleteBranch)
	return mux
}
