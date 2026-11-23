package model

// Apply returns a validated copy of item with the patch applied.
func (p ReservationPatch) Apply(item Reservation) (Reservation, error) {
	if p.BookID != nil {
		item.BookID = *p.BookID
	}
	if p.MemberID != nil {
		item.MemberID = *p.MemberID
	}
	if p.Requested != nil {
		item.Requested = *p.Requested
	}
	if p.Position != nil {
		item.Position = *p.Position
	}
	if p.Status != nil {
		item.Status = *p.Status
	}
	if p.Notes != nil {
		item.Notes = *p.Notes
	}
	err := item.Validate()
	return item, err
}

// Branch is a branch record.
type Branch struct {
	ID       int    `json:"id"`
	Name     string `json:"name"`
	City     string `json:"city"`
	Phone    string `json:"phone"`
	Opened   string `json:"opened"`
	Seats    int    `json:"seats"`
	OpenLate bool   `json:"open_late"`
}
