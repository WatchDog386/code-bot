package store

import "fleet-api/internal/model"

// MaxCost returns the record with the highest cost.
func (s *ServiceRecordStore) MaxCost() (model.ServiceRecord, bool) {
	var best model.ServiceRecord
	found := false
	for _, item := range s.List() {
		if !found || item.Cost > best.Cost {
			best, found = item, true
		}
	}
	return best, found
}

// WithKind returns records whose kind is value.
func (s *ServiceRecordStore) WithKind(value model.ServiceRecordKind) []model.ServiceRecord {
	return s.Filter(func(item model.ServiceRecord) bool { return item.Kind == value })
}

// CountByKind counts records for every kind.
func (s *ServiceRecordStore) CountByKind() map[model.ServiceRecordKind]int {
	counts := map[model.ServiceRecordKind]int{}
	for _, v := range model.ServiceRecordKindValues {
		counts[v] = 0
	}
	for _, item := range s.List() {
		counts[item.Kind]++
	}
	return counts
}

// FindByNotes returns records whose notes is exactly value.
func (s *ServiceRecordStore) FindByNotes(value string) []model.ServiceRecord {
	return s.Filter(func(item model.ServiceRecord) bool { return item.Notes == value })
}
