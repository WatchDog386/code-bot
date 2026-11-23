package store

import (
	"strings"
	"sync"

	"fleet-api/internal/model"
)

// AverageDistanceKm is the mean distance km (0 when there are no records).
func (s *TripStore) AverageDistanceKm() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalDistanceKm()) / float64(len(items))
}

// MaxDistanceKm returns the record with the highest distance km.
func (s *TripStore) MaxDistanceKm() (model.Trip, bool) {
	var best model.Trip
	found := false
	for _, item := range s.List() {
		if !found || item.DistanceKm > best.DistanceKm {
			best, found = item, true
		}
	}
	return best, found
}

// FindByPurpose returns records whose purpose is exactly value.
func (s *TripStore) FindByPurpose(value string) []model.Trip {
	return s.Filter(func(item model.Trip) bool { return item.Purpose == value })
}

// SearchPurpose returns records whose purpose contains text (any case).
func (s *TripStore) SearchPurpose(text string) []model.Trip {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Trip) bool { return strings.Contains(strings.ToLower(item.Purpose), needle) })
}

// WithStatus returns records whose status is value.
func (s *TripStore) WithStatus(value model.TripStatus) []model.Trip {
	return s.Filter(func(item model.Trip) bool { return item.Status == value })
}

// CountByStatus counts records for every status.
func (s *TripStore) CountByStatus() map[model.TripStatus]int {
	counts := map[model.TripStatus]int{}
	for _, v := range model.TripStatusValues {
		counts[v] = 0
	}
	for _, item := range s.List() {
		counts[item.Status]++
	}
	return counts
}

// Search returns records where any text field contains text (any case).
func (s *TripStore) Search(text string) []model.Trip {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Trip) bool {
		for _, value := range []string{item.Purpose} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// FuelLogStore keeps every fuel log.
type FuelLogStore struct {
	mu     sync.RWMutex
	items  map[int]model.FuelLog
	nextID int
}

// NewFuelLogStore returns an empty store.
func NewFuelLogStore() *FuelLogStore {
	return &FuelLogStore{items: map[int]model.FuelLog{}, nextID: 1}
}
