package model

import "math"

// TripPatch changes some fields of a Trip; nil means "leave as it is".
type TripPatch struct {
	VehicleID  *int        `json:"vehicle_id,omitempty"`
	DriverID   *int        `json:"driver_id,omitempty"`
	Started    *string     `json:"started,omitempty"`
	DistanceKm *float64    `json:"distance_km,omitempty"`
	Purpose    *string     `json:"purpose,omitempty"`
	Status     *TripStatus `json:"status,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p TripPatch) Apply(item Trip) (Trip, error) {
	if p.VehicleID != nil {
		item.VehicleID = *p.VehicleID
	}
	if p.DriverID != nil {
		item.DriverID = *p.DriverID
	}
	if p.Started != nil {
		item.Started = *p.Started
	}
	if p.DistanceKm != nil {
		item.DistanceKm = *p.DistanceKm
	}
	if p.Purpose != nil {
		item.Purpose = *p.Purpose
	}
	if p.Status != nil {
		item.Status = *p.Status
	}
	err := item.Validate()
	return item, err
}

// FuelLog is a fuel log record.
type FuelLog struct {
	ID        int     `json:"id"`
	VehicleID int     `json:"vehicle_id"`
	Filled    string  `json:"filled"`
	Litres    float64 `json:"litres"`
	Cost      float64 `json:"cost"`
	Station   string  `json:"station"`
}

// Validate checks every field and normalises text and amounts in place.
func (f *FuelLog) Validate() error {
	var err error
	if err = CheckRef("vehicle_id", f.VehicleID); err != nil {
		return err
	}
	if err = CheckDate("filled", f.Filled); err != nil {
		return err
	}
	if err = CheckNumber("litres", f.Litres); err != nil {
		return err
	}
	if err = CheckNumber("cost", f.Cost); err != nil {
		return err
	}
	f.Cost = math.Round(f.Cost*100) / 100
	if f.Station, err = CheckText("station", f.Station, 120, true); err != nil {
		return err
	}
	return nil
}
