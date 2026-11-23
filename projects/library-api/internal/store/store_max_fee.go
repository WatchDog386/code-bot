package store

import (
	"strings"
	"sync"

	"library-api/internal/model"
)

// MaxFee returns the record with the highest fee.
func (s *LoanStore) MaxFee() (model.Loan, bool) {
	var best model.Loan
	found := false
	for _, item := range s.List() {
		if !found || item.Fee > best.Fee {
			best, found = item, true
		}
	}
	return best, found
}

// Search returns records where any text field contains text (any case).
func (s *LoanStore) Search(text string) []model.Loan {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Loan) bool {
		return needle == ""
	})
}

// ReservationStore keeps every reservation.
type ReservationStore struct {
	mu     sync.RWMutex
	items  map[int]model.Reservation
	nextID int
}

// NewReservationStore returns an empty store.
func NewReservationStore() *ReservationStore {
	return &ReservationStore{items: map[int]model.Reservation{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *ReservationStore) Create(item model.Reservation) model.Reservation {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *ReservationStore) Get(id int) (model.Reservation, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}
