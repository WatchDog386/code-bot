package service_test

import (
	"errors"
	"strings"
	"testing"

	"fleet-api/internal/service"
)

func TestSearchDriverEmail(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetDriver(2)
	for _, item := range svc.Drivers.SearchEmail(strings.ToUpper(target.Email)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Email)
}

func TestSearchDriverLicenseNo(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetDriver(2)
	for _, item := range svc.Drivers.SearchLicenseNo(strings.ToUpper(target.LicenseNo)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.LicenseNo)
}

func TestDriverLicenseExpiryRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SampleDriver(2).LicenseExpiry
	total := len(svc.Drivers.LicenseExpiryBefore(day)) + len(svc.Drivers.LicenseExpiryOn(day)) + len(svc.Drivers.LicenseExpiryAfter(day))
	if total != svc.Drivers.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.Drivers.Count())
	}
}

func TestAdjustDriverRating(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetDriver(1)
	after, err := svc.AdjustDriverRating(1, 1.5)
	if err != nil || after.Rating-before.Rating < 1.49 || after.Rating-before.Rating > 1.51 {
		t.Fatalf("adjust = %v, %v", after.Rating, err)
	}
}

func TestToggleDriverOnDuty(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetDriver(1)
	after, err := svc.ToggleDriverOnDuty(1)
	if err != nil || after.OnDuty == before.OnDuty {
		t.Fatalf("toggle = %v, %v", after.OnDuty, err)
	}
}

func TestDeleteDriver(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateDriver(service.SampleDriver(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteDriver(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetDriver(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestDeleteDriverInUse(t *testing.T) {
	svc := seeded(t)
	if err := svc.DeleteDriver(1); !errors.Is(err, service.ErrConflict) {
		t.Fatalf("want ErrConflict, got %v", err)
	}
}

func TestDriverStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.DriverStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}
