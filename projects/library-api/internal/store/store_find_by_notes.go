package store

import (
	"sort"
	"strings"
	"sync"

	"library-api/internal/model"
)

// FindByNotes returns records whose notes is exactly value.
func (s *ReservationStore) FindByNotes(value string) []model.Reservation {
	return s.Filter(func(item model.Reservation) bool { return item.Notes == value })
}

// SearchNotes returns records whose notes contains text (any case).
func (s *ReservationStore) SearchNotes(text string) []model.Reservation {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Reservation) bool { return strings.Contains(strings.ToLower(item.Notes), needle) })
}

// Search returns records where any text field contains text (any case).
func (s *ReservationStore) Search(text string) []model.Reservation {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Reservation) bool {
		for _, value := range []string{item.Notes} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// BranchStore keeps every branch.
type BranchStore struct {
	mu     sync.RWMutex
	items  map[int]model.Branch
	nextID int
}

// NewBranchStore returns an empty store.
func NewBranchStore() *BranchStore {
	return &BranchStore{items: map[int]model.Branch{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *BranchStore) Create(item model.Branch) model.Branch {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *BranchStore) Get(id int) (model.Branch, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *BranchStore) List() []model.Branch {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.Branch, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}
