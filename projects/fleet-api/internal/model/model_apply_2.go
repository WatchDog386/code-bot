package model

import (
	"cmp"
	"fmt"
	"math"
)

// Apply returns a validated copy of item with the patch applied.
func (p FuelLogPatch) Apply(item FuelLog) (FuelLog, error) {
	if p.VehicleID != nil {
		item.VehicleID = *p.VehicleID
	}
	if p.Filled != nil {
		item.Filled = *p.Filled
	}
	if p.Litres != nil {
		item.Litres = *p.Litres
	}
	if p.Cost != nil {
		item.Cost = *p.Cost
	}
	if p.Station != nil {
		item.Station = *p.Station
	}
	err := item.Validate()
	return item, err
}

// ServiceRecord is a service record record.
type ServiceRecord struct {
	ID        int               `json:"id"`
	VehicleID int               `json:"vehicle_id"`
	Serviced  string            `json:"serviced"`
	Odometer  int               `json:"odometer"`
	Cost      float64           `json:"cost"`
	Kind      ServiceRecordKind `json:"kind"`
	Notes     string            `json:"notes"`
}

// Validate checks every field and normalises text and amounts in place.
func (s *ServiceRecord) Validate() error {
	var err error
	if err = CheckRef("vehicle_id", s.VehicleID); err != nil {
		return err
	}
	if err = CheckDate("serviced", s.Serviced); err != nil {
		return err
	}
	if err = CheckInt("odometer", s.Odometer); err != nil {
		return err
	}
	if err = CheckNumber("cost", s.Cost); err != nil {
		return err
	}
	s.Cost = math.Round(s.Cost*100) / 100
	if !s.Kind.Valid() {
		return Invalid("kind", "must be one of %s", ServiceRecordKindList())
	}
	if s.Notes, err = CheckText("notes", s.Notes, 2000, false); err != nil {
		return err
	}
	return nil
}

// Summary is one line for logs and lists.
func (s ServiceRecord) Summary() string {
	return fmt.Sprintf("ServiceRecord #%d", s.ID)
}

// Map is the record as plain values (for CSV export and templates).
func (s ServiceRecord) Map() map[string]any {
	return map[string]any{
		"id":         s.ID,
		"vehicle_id": s.VehicleID,
		"serviced":   s.Serviced,
		"odometer":   s.Odometer,
		"cost":       s.Cost,
		"kind":       string(s.Kind),
		"notes":      s.Notes,
	}
}

// CompareServiceRecordByVehicleID orders service records by vehicle id (for slices.SortFunc).
func CompareServiceRecordByVehicleID(a, b ServiceRecord) int {
	return cmp.Compare(a.VehicleID, b.VehicleID)
}

// CompareServiceRecordByServiced orders service records by serviced (for slices.SortFunc).
func CompareServiceRecordByServiced(a, b ServiceRecord) int {
	return cmp.Compare(a.Serviced, b.Serviced)
}
