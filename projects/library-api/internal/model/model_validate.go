package model

import (
	"cmp"
	"fmt"
)

// Validate checks every field and normalises text and amounts in place.
func (a *Author) Validate() error {
	var err error
	if a.Name, err = CheckText("name", a.Name, 120, true); err != nil {
		return err
	}
	if a.Email, err = CheckEmail("email", a.Email); err != nil {
		return err
	}
	if a.Country, err = CheckText("country", a.Country, 120, true); err != nil {
		return err
	}
	if err = CheckDate("born", a.Born); err != nil {
		return err
	}
	return nil
}

// Summary is one line for logs and lists.
func (a Author) Summary() string {
	return fmt.Sprintf("Author #%d: %s", a.ID, a.Name)
}

// Map is the record as plain values (for CSV export and templates).
func (a Author) Map() map[string]any {
	return map[string]any{
		"id":      a.ID,
		"name":    a.Name,
		"email":   a.Email,
		"country": a.Country,
		"born":    a.Born,
		"active":  a.Active,
	}
}

// CompareAuthorByName orders authors by name (for slices.SortFunc).
func CompareAuthorByName(a, b Author) int {
	return cmp.Compare(a.Name, b.Name)
}

// CompareAuthorByEmail orders authors by email (for slices.SortFunc).
func CompareAuthorByEmail(a, b Author) int {
	return cmp.Compare(a.Email, b.Email)
}
