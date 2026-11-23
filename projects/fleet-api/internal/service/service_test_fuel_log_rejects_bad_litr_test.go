package service_test

import (
	"errors"
	"strings"
	"testing"

	"fleet-api/internal/service"
)

func TestFuelLogRejectsBadLitres(t *testing.T) {
	svc := seeded(t)
	item := service.SampleFuelLog(12)
	item.Litres = -1
	_, err := svc.CreateFuelLog(item)
	wantField(t, err, "litres")
}

func TestFuelLogRejectsBadCost(t *testing.T) {
	svc := seeded(t)
	item := service.SampleFuelLog(12)
	item.Cost = -5
	_, err := svc.CreateFuelLog(item)
	wantField(t, err, "cost")
}

func TestFuelLogRejectsBadStation(t *testing.T) {
	svc := seeded(t)
	item := service.SampleFuelLog(12)
	item.Station = ""
	_, err := svc.CreateFuelLog(item)
	wantField(t, err, "station")
}

func TestFuelLogVehicleIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleFuelLog(13)
	item.VehicleID = 9999
	if _, err := svc.CreateFuelLog(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestFuelLogFilledRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SampleFuelLog(2).Filled
	total := len(svc.FuelLogs.FilledBefore(day)) + len(svc.FuelLogs.FilledOn(day)) + len(svc.FuelLogs.FilledAfter(day))
	if total != svc.FuelLogs.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.FuelLogs.Count())
	}
}

func TestAdjustFuelLogLitres(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetFuelLog(1)
	after, err := svc.AdjustFuelLogLitres(1, 1.5)
	if err != nil || after.Litres-before.Litres < 1.49 || after.Litres-before.Litres > 1.51 {
		t.Fatalf("adjust = %v, %v", after.Litres, err)
	}
}

func TestAdjustFuelLogCost(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetFuelLog(1)
	after, err := svc.AdjustFuelLogCost(1, 1.5)
	if err != nil || after.Cost-before.Cost < 1.49 || after.Cost-before.Cost > 1.51 {
		t.Fatalf("adjust = %v, %v", after.Cost, err)
	}
}

func TestSearchFuelLogStation(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetFuelLog(2)
	for _, item := range svc.FuelLogs.SearchStation(strings.ToUpper(target.Station)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Station)
}
