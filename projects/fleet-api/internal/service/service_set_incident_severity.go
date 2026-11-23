package service

import (
	"math"

	"fleet-api/internal/model"
)

// SetIncidentSeverity moves a incident to another severity.
func (s *Service) SetIncidentSeverity(id int, value model.IncidentSeverity) (model.Incident, error) {
	return s.UpdateIncident(id, model.IncidentPatch{Severity: &value})
}

// AdjustIncidentDamageCost adds delta to the damage cost of a incident (it can't go below zero).
func (s *Service) AdjustIncidentDamageCost(id int, delta float64) (model.Incident, error) {
	item, err := s.GetIncident(id)
	if err != nil {
		return model.Incident{}, err
	}
	value := math.Round((item.DamageCost+delta)*100) / 100
	return s.UpdateIncident(id, model.IncidentPatch{DamageCost: &value})
}

// ToggleIncidentReported flips the reported flag of a incident.
func (s *Service) ToggleIncidentReported(id int) (model.Incident, error) {
	item, err := s.GetIncident(id)
	if err != nil {
		return model.Incident{}, err
	}
	flipped := !item.Reported
	return s.UpdateIncident(id, model.IncidentPatch{Reported: &flipped})
}

// IncidentStats sums up every incident.
type IncidentStats struct {
	Count             int                            `json:"count"`
	BySeverity        map[model.IncidentSeverity]int `json:"by_severity"`
	TotalDamageCost   float64                        `json:"total_damage_cost"`
	AverageDamageCost float64                        `json:"average_damage_cost"`
	Reported          int                            `json:"reported"`
}
