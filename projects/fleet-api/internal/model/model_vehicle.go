package model

import "fmt"

// Vehicle is a vehicle record.
type Vehicle struct {
	ID      int         `json:"id"`
	Plate   string      `json:"plate"`
	Make    string      `json:"make"`
	Model   string      `json:"model"`
	Year    int         `json:"year"`
	Mileage int         `json:"mileage"`
	Fuel    VehicleFuel `json:"fuel"`
	Active  bool        `json:"active"`
}

// Validate checks every field and normalises text and amounts in place.
func (v *Vehicle) Validate() error {
	var err error
	if v.Plate, err = CheckText("plate", v.Plate, 120, true); err != nil {
		return err
	}
	if v.Make, err = CheckText("make", v.Make, 120, true); err != nil {
		return err
	}
	if v.Model, err = CheckText("model", v.Model, 120, true); err != nil {
		return err
	}
	if err = CheckInt("year", v.Year); err != nil {
		return err
	}
	if err = CheckInt("mileage", v.Mileage); err != nil {
		return err
	}
	if !v.Fuel.Valid() {
		return Invalid("fuel", "must be one of %s", VehicleFuelList())
	}
	return nil
}

// Summary is one line for logs and lists.
func (v Vehicle) Summary() string {
	return fmt.Sprintf("Vehicle #%d: %s", v.ID, v.Plate)
}
