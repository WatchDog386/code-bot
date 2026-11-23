package model

import "cmp"

// Map is the record as plain values (for CSV export and templates).
func (v Vehicle) Map() map[string]any {
	return map[string]any{
		"id":      v.ID,
		"plate":   v.Plate,
		"make":    v.Make,
		"model":   v.Model,
		"year":    v.Year,
		"mileage": v.Mileage,
		"fuel":    string(v.Fuel),
		"active":  v.Active,
	}
}

// CompareVehicleByPlate orders vehicles by plate (for slices.SortFunc).
func CompareVehicleByPlate(a, b Vehicle) int {
	return cmp.Compare(a.Plate, b.Plate)
}

// CompareVehicleByMake orders vehicles by make (for slices.SortFunc).
func CompareVehicleByMake(a, b Vehicle) int {
	return cmp.Compare(a.Make, b.Make)
}

// CompareVehicleByModel orders vehicles by model (for slices.SortFunc).
func CompareVehicleByModel(a, b Vehicle) int {
	return cmp.Compare(a.Model, b.Model)
}

// CompareVehicleByYear orders vehicles by year (for slices.SortFunc).
func CompareVehicleByYear(a, b Vehicle) int {
	return cmp.Compare(a.Year, b.Year)
}

// CompareVehicleByMileage orders vehicles by mileage (for slices.SortFunc).
func CompareVehicleByMileage(a, b Vehicle) int {
	return cmp.Compare(a.Mileage, b.Mileage)
}

// CompareVehicleByFuel orders vehicles by fuel (for slices.SortFunc).
func CompareVehicleByFuel(a, b Vehicle) int {
	return cmp.Compare(string(a.Fuel), string(b.Fuel))
}

// VehiclePatch changes some fields of a Vehicle; nil means "leave as it is".
type VehiclePatch struct {
	Plate   *string      `json:"plate,omitempty"`
	Make    *string      `json:"make,omitempty"`
	Model   *string      `json:"model,omitempty"`
	Year    *int         `json:"year,omitempty"`
	Mileage *int         `json:"mileage,omitempty"`
	Fuel    *VehicleFuel `json:"fuel,omitempty"`
	Active  *bool        `json:"active,omitempty"`
}
