package service

import (
	"fmt"
	"math"

	"fleet-api/internal/model"
)

// IncidentStats returns totals and breakdowns over every incident.
func (s *Service) IncidentStats() IncidentStats {
	return IncidentStats{
		Count:             s.Incidents.Count(),
		BySeverity:        s.Incidents.CountBySeverity(),
		TotalDamageCost:   s.Incidents.TotalDamageCost(),
		AverageDamageCost: s.Incidents.AverageDamageCost(),
		Reported:          len(s.Incidents.WhereReported(true)),
	}
}

// SampleIncident returns valid data for a new incident (links point at seeded records).
func SampleIncident(i int) model.Incident {
	return model.Incident{
		VehicleID:  (i-1)%3 + 1,
		DriverID:   (i-1)%3 + 1,
		Happened:   fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		Severity:   model.IncidentSeverityValues[i%3],
		DamageCost: math.Round((10*float64(i)+0.99)*100) / 100,
		Reported:   i%2 == 1,
	}
}
