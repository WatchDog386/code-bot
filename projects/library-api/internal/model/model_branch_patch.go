package model

// BranchPatch changes some fields of a Branch; nil means "leave as it is".
type BranchPatch struct {
	Name     *string `json:"name,omitempty"`
	City     *string `json:"city,omitempty"`
	Phone    *string `json:"phone,omitempty"`
	Opened   *string `json:"opened,omitempty"`
	Seats    *int    `json:"seats,omitempty"`
	OpenLate *bool   `json:"open_late,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p BranchPatch) Apply(item Branch) (Branch, error) {
	if p.Name != nil {
		item.Name = *p.Name
	}
	if p.City != nil {
		item.City = *p.City
	}
	if p.Phone != nil {
		item.Phone = *p.Phone
	}
	if p.Opened != nil {
		item.Opened = *p.Opened
	}
	if p.Seats != nil {
		item.Seats = *p.Seats
	}
	if p.OpenLate != nil {
		item.OpenLate = *p.OpenLate
	}
	err := item.Validate()
	return item, err
}
