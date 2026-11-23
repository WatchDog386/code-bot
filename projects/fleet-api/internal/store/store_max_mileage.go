package store

import (
	"strings"

	"fleet-api/internal/model"
)

// MaxMileage returns the record with the highest mileage.
func (s *VehicleStore) MaxMileage() (model.Vehicle, bool) {
	var best model.Vehicle
	found := false
	for _, item := range s.List() {
		if !found || item.Mileage > best.Mileage {
			best, found = item, true
		}
	}
	return best, found
}

// WithFuel returns records whose fuel is value.
func (s *VehicleStore) WithFuel(value model.VehicleFuel) []model.Vehicle {
	return s.Filter(func(item model.Vehicle) bool { return item.Fuel == value })
}

// CountByFuel counts records for every fuel.
func (s *VehicleStore) CountByFuel() map[model.VehicleFuel]int {
	counts := map[model.VehicleFuel]int{}
	for _, v := range model.VehicleFuelValues {
		counts[v] = 0
	}
	for _, item := range s.List() {
		counts[item.Fuel]++
	}
	return counts
}

// WhereActive returns records whose active flag equals flag.
func (s *VehicleStore) WhereActive(flag bool) []model.Vehicle {
	return s.Filter(func(item model.Vehicle) bool { return item.Active == flag })
}

// Search returns records where any text field contains text (any case).
func (s *VehicleStore) Search(text string) []model.Vehicle {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Vehicle) bool {
		for _, value := range []string{item.Plate, item.Make, item.Model} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}
