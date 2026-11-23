package store

import "fleet-api/internal/model"

// HappenedAfter returns records whose happened is after day (YYYY-MM-DD).
func (s *IncidentStore) HappenedAfter(day string) []model.Incident {
	return s.Filter(func(item model.Incident) bool { return item.Happened > day })
}

// HappenedOn returns records whose happened is day.
func (s *IncidentStore) HappenedOn(day string) []model.Incident {
	return s.Filter(func(item model.Incident) bool { return item.Happened == day })
}

// WithSeverity returns records whose severity is value.
func (s *IncidentStore) WithSeverity(value model.IncidentSeverity) []model.Incident {
	return s.Filter(func(item model.Incident) bool { return item.Severity == value })
}

// CountBySeverity counts records for every severity.
func (s *IncidentStore) CountBySeverity() map[model.IncidentSeverity]int {
	counts := map[model.IncidentSeverity]int{}
	for _, v := range model.IncidentSeverityValues {
		counts[v] = 0
	}
	for _, item := range s.List() {
		counts[item.Severity]++
	}
	return counts
}

// BetweenDamageCost returns records whose damage cost is within [low, high].
func (s *IncidentStore) BetweenDamageCost(low, high float64) []model.Incident {
	return s.Filter(func(item model.Incident) bool { return item.DamageCost >= low && item.DamageCost <= high })
}
