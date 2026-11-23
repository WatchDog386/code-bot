package store

import (
	"strings"
	"sync"

	"fleet-api/internal/model"
)

// FindByStation returns records whose station is exactly value.
func (s *FuelLogStore) FindByStation(value string) []model.FuelLog {
	return s.Filter(func(item model.FuelLog) bool { return item.Station == value })
}

// SearchStation returns records whose station contains text (any case).
func (s *FuelLogStore) SearchStation(text string) []model.FuelLog {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.FuelLog) bool { return strings.Contains(strings.ToLower(item.Station), needle) })
}

// Search returns records where any text field contains text (any case).
func (s *FuelLogStore) Search(text string) []model.FuelLog {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.FuelLog) bool {
		for _, value := range []string{item.Station} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// ServiceRecordStore keeps every service record.
type ServiceRecordStore struct {
	mu     sync.RWMutex
	items  map[int]model.ServiceRecord
	nextID int
}

// NewServiceRecordStore returns an empty store.
func NewServiceRecordStore() *ServiceRecordStore {
	return &ServiceRecordStore{items: map[int]model.ServiceRecord{}, nextID: 1}
}
