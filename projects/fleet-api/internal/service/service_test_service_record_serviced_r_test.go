package service_test

import (
	"errors"
	"strings"
	"testing"

	"fleet-api/internal/model"
	"fleet-api/internal/service"
)

func TestServiceRecordServicedRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SampleServiceRecord(2).Serviced
	total := len(svc.ServiceRecords.ServicedBefore(day)) + len(svc.ServiceRecords.ServicedOn(day)) + len(svc.ServiceRecords.ServicedAfter(day))
	if total != svc.ServiceRecords.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.ServiceRecords.Count())
	}
}

func TestAdjustServiceRecordOdometer(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetServiceRecord(1)
	after, err := svc.AdjustServiceRecordOdometer(1, 2)
	if err != nil || after.Odometer != before.Odometer+2 {
		t.Fatalf("adjust = %v, %v", after.Odometer, err)
	}
	_, err = svc.AdjustServiceRecordOdometer(1, -(after.Odometer + 100))
	wantField(t, err, "odometer")
}

func TestAdjustServiceRecordCost(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetServiceRecord(1)
	after, err := svc.AdjustServiceRecordCost(1, 1.5)
	if err != nil || after.Cost-before.Cost < 1.49 || after.Cost-before.Cost > 1.51 {
		t.Fatalf("adjust = %v, %v", after.Cost, err)
	}
}

func TestSetServiceRecordKind(t *testing.T) {
	svc := seeded(t)
	last := model.ServiceRecordKindValues[len(model.ServiceRecordKindValues)-1]
	item, err := svc.SetServiceRecordKind(1, last)
	if err != nil || item.Kind != last {
		t.Fatalf("set = %v, %v", item.Kind, err)
	}
	if got, want := svc.ServiceRecords.CountByKind()[last], len(svc.ServiceRecords.WithKind(last)); got != want {
		t.Fatalf("count %d != %d", got, want)
	}
}

func TestSearchServiceRecordNotes(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetServiceRecord(2)
	for _, item := range svc.ServiceRecords.SearchNotes(strings.ToUpper(target.Notes)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Notes)
}

func TestDeleteServiceRecord(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateServiceRecord(service.SampleServiceRecord(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteServiceRecord(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetServiceRecord(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}
