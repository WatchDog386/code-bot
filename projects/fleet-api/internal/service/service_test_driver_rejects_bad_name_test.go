package service_test

import (
	"strings"
	"testing"

	"fleet-api/internal/service"
)

func TestDriverRejectsBadName(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDriver(12)
	item.Name = ""
	_, err := svc.CreateDriver(item)
	wantField(t, err, "name")
}

func TestDriverRejectsBadEmail(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDriver(12)
	item.Email = "not-an-email"
	_, err := svc.CreateDriver(item)
	wantField(t, err, "email")
}

func TestDriverRejectsBadLicenseNo(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDriver(12)
	item.LicenseNo = ""
	_, err := svc.CreateDriver(item)
	wantField(t, err, "license_no")
}

func TestDriverRejectsBadLicenseExpiry(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDriver(12)
	item.LicenseExpiry = "2026-02-30"
	_, err := svc.CreateDriver(item)
	wantField(t, err, "license_expiry")
}

func TestDriverRejectsBadRating(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDriver(12)
	item.Rating = -1
	_, err := svc.CreateDriver(item)
	wantField(t, err, "rating")
}

func TestSearchDriverName(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetDriver(2)
	for _, item := range svc.Drivers.SearchName(strings.ToUpper(target.Name)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Name)
}
