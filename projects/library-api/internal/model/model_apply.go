package model

import "math"

// Apply returns a validated copy of item with the patch applied.
func (p BookPatch) Apply(item Book) (Book, error) {
	if p.Title != nil {
		item.Title = *p.Title
	}
	if p.AuthorID != nil {
		item.AuthorID = *p.AuthorID
	}
	if p.Isbn != nil {
		item.Isbn = *p.Isbn
	}
	if p.Pages != nil {
		item.Pages = *p.Pages
	}
	if p.Price != nil {
		item.Price = *p.Price
	}
	if p.Published != nil {
		item.Published = *p.Published
	}
	if p.Genre != nil {
		item.Genre = *p.Genre
	}
	if p.Available != nil {
		item.Available = *p.Available
	}
	err := item.Validate()
	return item, err
}

// Member is a member record.
type Member struct {
	ID     int        `json:"id"`
	Name   string     `json:"name"`
	Email  string     `json:"email"`
	Phone  string     `json:"phone"`
	Joined string     `json:"joined"`
	Tier   MemberTier `json:"tier"`
	Fines  float64    `json:"fines"`
	Active bool       `json:"active"`
}

// Validate checks every field and normalises text and amounts in place.
func (m *Member) Validate() error {
	var err error
	if m.Name, err = CheckText("name", m.Name, 120, true); err != nil {
		return err
	}
	if m.Email, err = CheckEmail("email", m.Email); err != nil {
		return err
	}
	if m.Phone, err = CheckText("phone", m.Phone, 120, true); err != nil {
		return err
	}
	if err = CheckDate("joined", m.Joined); err != nil {
		return err
	}
	if !m.Tier.Valid() {
		return Invalid("tier", "must be one of %s", MemberTierList())
	}
	if err = CheckNumber("fines", m.Fines); err != nil {
		return err
	}
	m.Fines = math.Round(m.Fines*100) / 100
	return nil
}
