package store

import (
	"strings"

	"fleet-api/internal/model"
)

// FindByMake returns records whose make is exactly value.
func (s *VehicleStore) FindByMake(value string) []model.Vehicle {
	return s.Filter(func(item model.Vehicle) bool { return item.Make == value })
}

// SearchMake returns records whose make contains text (any case).
func (s *VehicleStore) SearchMake(text string) []model.Vehicle {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Vehicle) bool { return strings.Contains(strings.ToLower(item.Make), needle) })
}

// FindByModel returns records whose model is exactly value.
func (s *VehicleStore) FindByModel(value string) []model.Vehicle {
	return s.Filter(func(item model.Vehicle) bool { return item.Model == value })
}

// SearchModel returns records whose model contains text (any case).
func (s *VehicleStore) SearchModel(text string) []model.Vehicle {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Vehicle) bool { return strings.Contains(strings.ToLower(item.Model), needle) })
}

// BetweenYear returns records whose year is within [low, high].
func (s *VehicleStore) BetweenYear(low, high int) []model.Vehicle {
	return s.Filter(func(item model.Vehicle) bool { return item.Year >= low && item.Year <= high })
}

// TotalYear adds up the year of every record.
func (s *VehicleStore) TotalYear() int {
	var total int
	for _, item := range s.List() {
		total += item.Year
	}
	return total
}

// AverageYear is the mean year (0 when there are no records).
func (s *VehicleStore) AverageYear() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalYear()) / float64(len(items))
}
