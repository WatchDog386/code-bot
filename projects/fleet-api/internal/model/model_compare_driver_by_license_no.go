package model

import "cmp"

// CompareDriverByLicenseNo orders drivers by license no (for slices.SortFunc).
func CompareDriverByLicenseNo(a, b Driver) int {
	return cmp.Compare(a.LicenseNo, b.LicenseNo)
}

// CompareDriverByLicenseExpiry orders drivers by license expiry (for slices.SortFunc).
func CompareDriverByLicenseExpiry(a, b Driver) int {
	return cmp.Compare(a.LicenseExpiry, b.LicenseExpiry)
}

// CompareDriverByRating orders drivers by rating (for slices.SortFunc).
func CompareDriverByRating(a, b Driver) int {
	return cmp.Compare(a.Rating, b.Rating)
}

// DriverPatch changes some fields of a Driver; nil means "leave as it is".
type DriverPatch struct {
	Name          *string  `json:"name,omitempty"`
	Email         *string  `json:"email,omitempty"`
	LicenseNo     *string  `json:"license_no,omitempty"`
	LicenseExpiry *string  `json:"license_expiry,omitempty"`
	Rating        *float64 `json:"rating,omitempty"`
	OnDuty        *bool    `json:"on_duty,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p DriverPatch) Apply(item Driver) (Driver, error) {
	if p.Name != nil {
		item.Name = *p.Name
	}
	if p.Email != nil {
		item.Email = *p.Email
	}
	if p.LicenseNo != nil {
		item.LicenseNo = *p.LicenseNo
	}
	if p.LicenseExpiry != nil {
		item.LicenseExpiry = *p.LicenseExpiry
	}
	if p.Rating != nil {
		item.Rating = *p.Rating
	}
	if p.OnDuty != nil {
		item.OnDuty = *p.OnDuty
	}
	err := item.Validate()
	return item, err
}

// Trip is a trip record.
type Trip struct {
	ID         int        `json:"id"`
	VehicleID  int        `json:"vehicle_id"`
	DriverID   int        `json:"driver_id"`
	Started    string     `json:"started"`
	DistanceKm float64    `json:"distance_km"`
	Purpose    string     `json:"purpose"`
	Status     TripStatus `json:"status"`
}
