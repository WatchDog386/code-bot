package model

import (
	"cmp"
	"fmt"
)

// Driver is a driver record.
type Driver struct {
	ID            int     `json:"id"`
	Name          string  `json:"name"`
	Email         string  `json:"email"`
	LicenseNo     string  `json:"license_no"`
	LicenseExpiry string  `json:"license_expiry"`
	Rating        float64 `json:"rating"`
	OnDuty        bool    `json:"on_duty"`
}

// Validate checks every field and normalises text and amounts in place.
func (d *Driver) Validate() error {
	var err error
	if d.Name, err = CheckText("name", d.Name, 120, true); err != nil {
		return err
	}
	if d.Email, err = CheckEmail("email", d.Email); err != nil {
		return err
	}
	if d.LicenseNo, err = CheckText("license_no", d.LicenseNo, 120, true); err != nil {
		return err
	}
	if err = CheckDate("license_expiry", d.LicenseExpiry); err != nil {
		return err
	}
	if err = CheckNumber("rating", d.Rating); err != nil {
		return err
	}
	return nil
}

// Summary is one line for logs and lists.
func (d Driver) Summary() string {
	return fmt.Sprintf("Driver #%d: %s", d.ID, d.Name)
}

// Map is the record as plain values (for CSV export and templates).
func (d Driver) Map() map[string]any {
	return map[string]any{
		"id":             d.ID,
		"name":           d.Name,
		"email":          d.Email,
		"license_no":     d.LicenseNo,
		"license_expiry": d.LicenseExpiry,
		"rating":         d.Rating,
		"on_duty":        d.OnDuty,
	}
}

// CompareDriverByName orders drivers by name (for slices.SortFunc).
func CompareDriverByName(a, b Driver) int {
	return cmp.Compare(a.Name, b.Name)
}

// CompareDriverByEmail orders drivers by email (for slices.SortFunc).
func CompareDriverByEmail(a, b Driver) int {
	return cmp.Compare(a.Email, b.Email)
}
