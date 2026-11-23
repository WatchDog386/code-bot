package store

import (
	"strings"

	"fleet-api/internal/model"
)

// SearchName returns records whose name contains text (any case).
func (s *DriverStore) SearchName(text string) []model.Driver {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Driver) bool { return strings.Contains(strings.ToLower(item.Name), needle) })
}

// FindByEmail returns records whose email is exactly value.
func (s *DriverStore) FindByEmail(value string) []model.Driver {
	return s.Filter(func(item model.Driver) bool { return item.Email == value })
}

// SearchEmail returns records whose email contains text (any case).
func (s *DriverStore) SearchEmail(text string) []model.Driver {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Driver) bool { return strings.Contains(strings.ToLower(item.Email), needle) })
}

// FindByLicenseNo returns records whose license no is exactly value.
func (s *DriverStore) FindByLicenseNo(value string) []model.Driver {
	return s.Filter(func(item model.Driver) bool { return item.LicenseNo == value })
}

// SearchLicenseNo returns records whose license no contains text (any case).
func (s *DriverStore) SearchLicenseNo(text string) []model.Driver {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Driver) bool { return strings.Contains(strings.ToLower(item.LicenseNo), needle) })
}

// LicenseExpiryBefore returns records whose license expiry is before day (YYYY-MM-DD).
func (s *DriverStore) LicenseExpiryBefore(day string) []model.Driver {
	return s.Filter(func(item model.Driver) bool { return item.LicenseExpiry < day })
}

// LicenseExpiryAfter returns records whose license expiry is after day (YYYY-MM-DD).
func (s *DriverStore) LicenseExpiryAfter(day string) []model.Driver {
	return s.Filter(func(item model.Driver) bool { return item.LicenseExpiry > day })
}

// LicenseExpiryOn returns records whose license expiry is day.
func (s *DriverStore) LicenseExpiryOn(day string) []model.Driver {
	return s.Filter(func(item model.Driver) bool { return item.LicenseExpiry == day })
}

// BetweenRating returns records whose rating is within [low, high].
func (s *DriverStore) BetweenRating(low, high float64) []model.Driver {
	return s.Filter(func(item model.Driver) bool { return item.Rating >= low && item.Rating <= high })
}

// TotalRating adds up the rating of every record.
func (s *DriverStore) TotalRating() float64 {
	var total float64
	for _, item := range s.List() {
		total += item.Rating
	}
	return total
}
