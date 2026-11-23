package store

import "fleet-api/internal/model"

// Count is the number of records.
func (s *ServiceRecordStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *ServiceRecordStore) Filter(keep func(model.ServiceRecord) bool) []model.ServiceRecord {
	out := []model.ServiceRecord{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// ForVehicle returns records linked to vehicle id.
func (s *ServiceRecordStore) ForVehicle(id int) []model.ServiceRecord {
	return s.Filter(func(item model.ServiceRecord) bool { return item.VehicleID == id })
}

// CountForVehicle counts records linked to vehicle id.
func (s *ServiceRecordStore) CountForVehicle(id int) int {
	return len(s.ForVehicle(id))
}

// ServicedBefore returns records whose serviced is before day (YYYY-MM-DD).
func (s *ServiceRecordStore) ServicedBefore(day string) []model.ServiceRecord {
	return s.Filter(func(item model.ServiceRecord) bool { return item.Serviced < day })
}

// ServicedAfter returns records whose serviced is after day (YYYY-MM-DD).
func (s *ServiceRecordStore) ServicedAfter(day string) []model.ServiceRecord {
	return s.Filter(func(item model.ServiceRecord) bool { return item.Serviced > day })
}

// ServicedOn returns records whose serviced is day.
func (s *ServiceRecordStore) ServicedOn(day string) []model.ServiceRecord {
	return s.Filter(func(item model.ServiceRecord) bool { return item.Serviced == day })
}

// BetweenOdometer returns records whose odometer is within [low, high].
func (s *ServiceRecordStore) BetweenOdometer(low, high int) []model.ServiceRecord {
	return s.Filter(func(item model.ServiceRecord) bool { return item.Odometer >= low && item.Odometer <= high })
}

// TotalOdometer adds up the odometer of every record.
func (s *ServiceRecordStore) TotalOdometer() int {
	var total int
	for _, item := range s.List() {
		total += item.Odometer
	}
	return total
}
