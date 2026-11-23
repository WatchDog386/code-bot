package model

import "cmp"

// CompareServiceRecordByOdometer orders service records by odometer (for slices.SortFunc).
func CompareServiceRecordByOdometer(a, b ServiceRecord) int {
	return cmp.Compare(a.Odometer, b.Odometer)
}

// CompareServiceRecordByCost orders service records by cost (for slices.SortFunc).
func CompareServiceRecordByCost(a, b ServiceRecord) int {
	return cmp.Compare(a.Cost, b.Cost)
}

// CompareServiceRecordByKind orders service records by kind (for slices.SortFunc).
func CompareServiceRecordByKind(a, b ServiceRecord) int {
	return cmp.Compare(string(a.Kind), string(b.Kind))
}

// CompareServiceRecordByNotes orders service records by notes (for slices.SortFunc).
func CompareServiceRecordByNotes(a, b ServiceRecord) int {
	return cmp.Compare(a.Notes, b.Notes)
}

// ServiceRecordPatch changes some fields of a ServiceRecord; nil means "leave as it is".
type ServiceRecordPatch struct {
	VehicleID *int               `json:"vehicle_id,omitempty"`
	Serviced  *string            `json:"serviced,omitempty"`
	Odometer  *int               `json:"odometer,omitempty"`
	Cost      *float64           `json:"cost,omitempty"`
	Kind      *ServiceRecordKind `json:"kind,omitempty"`
	Notes     *string            `json:"notes,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p ServiceRecordPatch) Apply(item ServiceRecord) (ServiceRecord, error) {
	if p.VehicleID != nil {
		item.VehicleID = *p.VehicleID
	}
	if p.Serviced != nil {
		item.Serviced = *p.Serviced
	}
	if p.Odometer != nil {
		item.Odometer = *p.Odometer
	}
	if p.Cost != nil {
		item.Cost = *p.Cost
	}
	if p.Kind != nil {
		item.Kind = *p.Kind
	}
	if p.Notes != nil {
		item.Notes = *p.Notes
	}
	err := item.Validate()
	return item, err
}
