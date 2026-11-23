// Package service holds the Library Circulation business rules: validation, links between
// records, small domain operations and statistics.
package service

import (
	"errors"
	"fmt"

	"library-api/internal/store"
)

// Errors the service returns (wrapped with details).
var (
	ErrNotFound = errors.New("not found")
	ErrConflict = errors.New("conflict")
)

func notFound(entity string, id int) error {
	return fmt.Errorf("%s %d: %w", entity, id, ErrNotFound)
}

func inUse(entity string, id, n int, by string) error {
	return fmt.Errorf("%s %d is still used by %d %s: %w", entity, id, n, by, ErrConflict)
}

// Service is the whole application: every store plus the rules between them.
type Service struct {
	Authors      *store.AuthorStore
	Books        *store.BookStore
	Members      *store.MemberStore
	Loans        *store.LoanStore
	Reservations *store.ReservationStore
	Branches     *store.BranchStore
}

// New returns a service with empty stores.
func New() *Service {
	return &Service{
		Authors:      store.NewAuthorStore(),
		Books:        store.NewBookStore(),
		Members:      store.NewMemberStore(),
		Loans:        store.NewLoanStore(),
		Reservations: store.NewReservationStore(),
		Branches:     store.NewBranchStore(),
	}
}

// Seed creates n sample records of every kind.
func (s *Service) Seed(n int) error {
	for i := 1; i <= n; i++ {
		if _, err := s.CreateAuthor(SampleAuthor(i)); err != nil {
			return err
		}
		if _, err := s.CreateBook(SampleBook(i)); err != nil {
			return err
		}
		if _, err := s.CreateMember(SampleMember(i)); err != nil {
			return err
		}
		if _, err := s.CreateLoan(SampleLoan(i)); err != nil {
			return err
		}
		if _, err := s.CreateReservation(SampleReservation(i)); err != nil {
			return err
		}
		if _, err := s.CreateBranch(SampleBranch(i)); err != nil {
			return err
		}
	}
	return nil
}
