package store

import (
	"strings"
	"sync"

	"fleet-api/internal/model"
)

// AverageRating is the mean rating (0 when there are no records).
func (s *DriverStore) AverageRating() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalRating()) / float64(len(items))
}

// MaxRating returns the record with the highest rating.
func (s *DriverStore) MaxRating() (model.Driver, bool) {
	var best model.Driver
	found := false
	for _, item := range s.List() {
		if !found || item.Rating > best.Rating {
			best, found = item, true
		}
	}
	return best, found
}

// WhereOnDuty returns records whose on duty flag equals flag.
func (s *DriverStore) WhereOnDuty(flag bool) []model.Driver {
	return s.Filter(func(item model.Driver) bool { return item.OnDuty == flag })
}

// Search returns records where any text field contains text (any case).
func (s *DriverStore) Search(text string) []model.Driver {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Driver) bool {
		for _, value := range []string{item.Name, item.Email, item.LicenseNo} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// TripStore keeps every trip.
type TripStore struct {
	mu     sync.RWMutex
	items  map[int]model.Trip
	nextID int
}

// NewTripStore returns an empty store.
func NewTripStore() *TripStore {
	return &TripStore{items: map[int]model.Trip{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *TripStore) Create(item model.Trip) model.Trip {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *TripStore) Get(id int) (model.Trip, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}
