package store

import (
	"sort"
	"strings"
	"sync"

	"fleet-api/internal/model"
)

// SearchNotes returns records whose notes contains text (any case).
func (s *ServiceRecordStore) SearchNotes(text string) []model.ServiceRecord {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.ServiceRecord) bool { return strings.Contains(strings.ToLower(item.Notes), needle) })
}

// Search returns records where any text field contains text (any case).
func (s *ServiceRecordStore) Search(text string) []model.ServiceRecord {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.ServiceRecord) bool {
		for _, value := range []string{item.Notes} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// IncidentStore keeps every incident.
type IncidentStore struct {
	mu     sync.RWMutex
	items  map[int]model.Incident
	nextID int
}

// NewIncidentStore returns an empty store.
func NewIncidentStore() *IncidentStore {
	return &IncidentStore{items: map[int]model.Incident{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *IncidentStore) Create(item model.Incident) model.Incident {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *IncidentStore) Get(id int) (model.Incident, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *IncidentStore) List() []model.Incident {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.Incident, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}
