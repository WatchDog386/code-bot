package model

// Apply returns a validated copy of item with the patch applied.
func (p VehiclePatch) Apply(item Vehicle) (Vehicle, error) {
	if p.Plate != nil {
		item.Plate = *p.Plate
	}
	if p.Make != nil {
		item.Make = *p.Make
	}
	if p.Model != nil {
		item.Model = *p.Model
	}
	if p.Year != nil {
		item.Year = *p.Year
	}
	if p.Mileage != nil {
		item.Mileage = *p.Mileage
	}
	if p.Fuel != nil {
		item.Fuel = *p.Fuel
	}
	if p.Active != nil {
		item.Active = *p.Active
	}
	err := item.Validate()
	return item, err
}
