package model

import (
	"cmp"
	"fmt"
)

// Summary is one line for logs and lists.
func (f FuelLog) Summary() string {
	return fmt.Sprintf("FuelLog #%d: %s", f.ID, f.Station)
}

// Map is the record as plain values (for CSV export and templates).
func (f FuelLog) Map() map[string]any {
	return map[string]any{
		"id":         f.ID,
		"vehicle_id": f.VehicleID,
		"filled":     f.Filled,
		"litres":     f.Litres,
		"cost":       f.Cost,
		"station":    f.Station,
	}
}

// CompareFuelLogByVehicleID orders fuel logs by vehicle id (for slices.SortFunc).
func CompareFuelLogByVehicleID(a, b FuelLog) int {
	return cmp.Compare(a.VehicleID, b.VehicleID)
}

// CompareFuelLogByFilled orders fuel logs by filled (for slices.SortFunc).
func CompareFuelLogByFilled(a, b FuelLog) int {
	return cmp.Compare(a.Filled, b.Filled)
}

// CompareFuelLogByLitres orders fuel logs by litres (for slices.SortFunc).
func CompareFuelLogByLitres(a, b FuelLog) int {
	return cmp.Compare(a.Litres, b.Litres)
}

// CompareFuelLogByCost orders fuel logs by cost (for slices.SortFunc).
func CompareFuelLogByCost(a, b FuelLog) int {
	return cmp.Compare(a.Cost, b.Cost)
}

// CompareFuelLogByStation orders fuel logs by station (for slices.SortFunc).
func CompareFuelLogByStation(a, b FuelLog) int {
	return cmp.Compare(a.Station, b.Station)
}

// FuelLogPatch changes some fields of a FuelLog; nil means "leave as it is".
type FuelLogPatch struct {
	VehicleID *int     `json:"vehicle_id,omitempty"`
	Filled    *string  `json:"filled,omitempty"`
	Litres    *float64 `json:"litres,omitempty"`
	Cost      *float64 `json:"cost,omitempty"`
	Station   *string  `json:"station,omitempty"`
}
