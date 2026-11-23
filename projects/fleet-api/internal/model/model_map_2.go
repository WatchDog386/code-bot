package model

import "cmp"

// Map is the record as plain values (for CSV export and templates).
func (i Incident) Map() map[string]any {
	return map[string]any{
		"id":          i.ID,
		"vehicle_id":  i.VehicleID,
		"driver_id":   i.DriverID,
		"happened":    i.Happened,
		"severity":    string(i.Severity),
		"damage_cost": i.DamageCost,
		"reported":    i.Reported,
	}
}

// CompareIncidentByVehicleID orders incidents by vehicle id (for slices.SortFunc).
func CompareIncidentByVehicleID(a, b Incident) int {
	return cmp.Compare(a.VehicleID, b.VehicleID)
}

// CompareIncidentByDriverID orders incidents by driver id (for slices.SortFunc).
func CompareIncidentByDriverID(a, b Incident) int {
	return cmp.Compare(a.DriverID, b.DriverID)
}

// CompareIncidentByHappened orders incidents by happened (for slices.SortFunc).
func CompareIncidentByHappened(a, b Incident) int {
	return cmp.Compare(a.Happened, b.Happened)
}

// CompareIncidentBySeverity orders incidents by severity (for slices.SortFunc).
func CompareIncidentBySeverity(a, b Incident) int {
	return cmp.Compare(string(a.Severity), string(b.Severity))
}

// CompareIncidentByDamageCost orders incidents by damage cost (for slices.SortFunc).
func CompareIncidentByDamageCost(a, b Incident) int {
	return cmp.Compare(a.DamageCost, b.DamageCost)
}

// IncidentPatch changes some fields of a Incident; nil means "leave as it is".
type IncidentPatch struct {
	VehicleID  *int              `json:"vehicle_id,omitempty"`
	DriverID   *int              `json:"driver_id,omitempty"`
	Happened   *string           `json:"happened,omitempty"`
	Severity   *IncidentSeverity `json:"severity,omitempty"`
	DamageCost *float64          `json:"damage_cost,omitempty"`
	Reported   *bool             `json:"reported,omitempty"`
}
