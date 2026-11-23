package model

import (
	"fmt"
	"math"
)

// Incident is a incident record.
type Incident struct {
	ID         int              `json:"id"`
	VehicleID  int              `json:"vehicle_id"`
	DriverID   int              `json:"driver_id"`
	Happened   string           `json:"happened"`
	Severity   IncidentSeverity `json:"severity"`
	DamageCost float64          `json:"damage_cost"`
	Reported   bool             `json:"reported"`
}

// Validate checks every field and normalises text and amounts in place.
func (i *Incident) Validate() error {
	var err error
	if err = CheckRef("vehicle_id", i.VehicleID); err != nil {
		return err
	}
	if err = CheckRef("driver_id", i.DriverID); err != nil {
		return err
	}
	if err = CheckDate("happened", i.Happened); err != nil {
		return err
	}
	if !i.Severity.Valid() {
		return Invalid("severity", "must be one of %s", IncidentSeverityList())
	}
	if err = CheckNumber("damage_cost", i.DamageCost); err != nil {
		return err
	}
	i.DamageCost = math.Round(i.DamageCost*100) / 100
	return nil
}

// Summary is one line for logs and lists.
func (i Incident) Summary() string {
	return fmt.Sprintf("Incident #%d", i.ID)
}
