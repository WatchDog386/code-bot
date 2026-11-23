package model

// Apply returns a validated copy of item with the patch applied.
func (p IncidentPatch) Apply(item Incident) (Incident, error) {
	if p.VehicleID != nil {
		item.VehicleID = *p.VehicleID
	}
	if p.DriverID != nil {
		item.DriverID = *p.DriverID
	}
	if p.Happened != nil {
		item.Happened = *p.Happened
	}
	if p.Severity != nil {
		item.Severity = *p.Severity
	}
	if p.DamageCost != nil {
		item.DamageCost = *p.DamageCost
	}
	if p.Reported != nil {
		item.Reported = *p.Reported
	}
	err := item.Validate()
	return item, err
}
