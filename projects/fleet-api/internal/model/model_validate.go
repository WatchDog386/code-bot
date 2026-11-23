package model

import (
	"cmp"
	"fmt"
)

// Validate checks every field and normalises text and amounts in place.
func (t *Trip) Validate() error {
	var err error
	if err = CheckRef("vehicle_id", t.VehicleID); err != nil {
		return err
	}
	if err = CheckRef("driver_id", t.DriverID); err != nil {
		return err
	}
	if err = CheckDate("started", t.Started); err != nil {
		return err
	}
	if err = CheckNumber("distance_km", t.DistanceKm); err != nil {
		return err
	}
	if t.Purpose, err = CheckText("purpose", t.Purpose, 120, true); err != nil {
		return err
	}
	if !t.Status.Valid() {
		return Invalid("status", "must be one of %s", TripStatusList())
	}
	return nil
}

// Summary is one line for logs and lists.
func (t Trip) Summary() string {
	return fmt.Sprintf("Trip #%d: %s", t.ID, t.Purpose)
}

// Map is the record as plain values (for CSV export and templates).
func (t Trip) Map() map[string]any {
	return map[string]any{
		"id":          t.ID,
		"vehicle_id":  t.VehicleID,
		"driver_id":   t.DriverID,
		"started":     t.Started,
		"distance_km": t.DistanceKm,
		"purpose":     t.Purpose,
		"status":      string(t.Status),
	}
}

// CompareTripByVehicleID orders trips by vehicle id (for slices.SortFunc).
func CompareTripByVehicleID(a, b Trip) int {
	return cmp.Compare(a.VehicleID, b.VehicleID)
}

// CompareTripByDriverID orders trips by driver id (for slices.SortFunc).
func CompareTripByDriverID(a, b Trip) int {
	return cmp.Compare(a.DriverID, b.DriverID)
}

// CompareTripByStarted orders trips by started (for slices.SortFunc).
func CompareTripByStarted(a, b Trip) int {
	return cmp.Compare(a.Started, b.Started)
}

// CompareTripByDistanceKm orders trips by distance km (for slices.SortFunc).
func CompareTripByDistanceKm(a, b Trip) int {
	return cmp.Compare(a.DistanceKm, b.DistanceKm)
}

// CompareTripByPurpose orders trips by purpose (for slices.SortFunc).
func CompareTripByPurpose(a, b Trip) int {
	return cmp.Compare(a.Purpose, b.Purpose)
}

// CompareTripByStatus orders trips by status (for slices.SortFunc).
func CompareTripByStatus(a, b Trip) int {
	return cmp.Compare(string(a.Status), string(b.Status))
}
