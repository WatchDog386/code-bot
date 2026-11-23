package service_test

import (
	"errors"
	"testing"

	"fleet-api/internal/model"
	"fleet-api/internal/service"
)

func TestIncidentHappenedRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SampleIncident(2).Happened
	total := len(svc.Incidents.HappenedBefore(day)) + len(svc.Incidents.HappenedOn(day)) + len(svc.Incidents.HappenedAfter(day))
	if total != svc.Incidents.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.Incidents.Count())
	}
}

func TestSetIncidentSeverity(t *testing.T) {
	svc := seeded(t)
	last := model.IncidentSeverityValues[len(model.IncidentSeverityValues)-1]
	item, err := svc.SetIncidentSeverity(1, last)
	if err != nil || item.Severity != last {
		t.Fatalf("set = %v, %v", item.Severity, err)
	}
	if got, want := svc.Incidents.CountBySeverity()[last], len(svc.Incidents.WithSeverity(last)); got != want {
		t.Fatalf("count %d != %d", got, want)
	}
}

func TestAdjustIncidentDamageCost(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetIncident(1)
	after, err := svc.AdjustIncidentDamageCost(1, 1.5)
	if err != nil || after.DamageCost-before.DamageCost < 1.49 || after.DamageCost-before.DamageCost > 1.51 {
		t.Fatalf("adjust = %v, %v", after.DamageCost, err)
	}
}

func TestToggleIncidentReported(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetIncident(1)
	after, err := svc.ToggleIncidentReported(1)
	if err != nil || after.Reported == before.Reported {
		t.Fatalf("toggle = %v, %v", after.Reported, err)
	}
}

func TestDeleteIncident(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateIncident(service.SampleIncident(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteIncident(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetIncident(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestIncidentStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.IncidentStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}
