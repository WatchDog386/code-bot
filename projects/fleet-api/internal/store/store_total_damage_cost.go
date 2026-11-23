package store

import (
	"strings"

	"fleet-api/internal/model"
)

// TotalDamageCost adds up the damage cost of every record.
func (s *IncidentStore) TotalDamageCost() float64 {
	var total float64
	for _, item := range s.List() {
		total += item.DamageCost
	}
	return total
}

// AverageDamageCost is the mean damage cost (0 when there are no records).
func (s *IncidentStore) AverageDamageCost() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalDamageCost()) / float64(len(items))
}

// MaxDamageCost returns the record with the highest damage cost.
func (s *IncidentStore) MaxDamageCost() (model.Incident, bool) {
	var best model.Incident
	found := false
	for _, item := range s.List() {
		if !found || item.DamageCost > best.DamageCost {
			best, found = item, true
		}
	}
	return best, found
}

// WhereReported returns records whose reported flag equals flag.
func (s *IncidentStore) WhereReported(flag bool) []model.Incident {
	return s.Filter(func(item model.Incident) bool { return item.Reported == flag })
}

// Search returns records where any text field contains text (any case).
func (s *IncidentStore) Search(text string) []model.Incident {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Incident) bool {
		return needle == ""
	})
}
