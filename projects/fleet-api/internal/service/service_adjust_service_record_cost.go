package service

import (
	"fmt"
	"math"

	"fleet-api/internal/model"
)

// AdjustServiceRecordCost adds delta to the cost of a service record (it can't go below zero).
func (s *Service) AdjustServiceRecordCost(id int, delta float64) (model.ServiceRecord, error) {
	item, err := s.GetServiceRecord(id)
	if err != nil {
		return model.ServiceRecord{}, err
	}
	value := math.Round((item.Cost+delta)*100) / 100
	return s.UpdateServiceRecord(id, model.ServiceRecordPatch{Cost: &value})
}

// SetServiceRecordKind moves a service record to another kind.
func (s *Service) SetServiceRecordKind(id int, value model.ServiceRecordKind) (model.ServiceRecord, error) {
	return s.UpdateServiceRecord(id, model.ServiceRecordPatch{Kind: &value})
}

// ServiceRecordStats sums up every service record.
type ServiceRecordStats struct {
	Count           int                             `json:"count"`
	TotalOdometer   int                             `json:"total_odometer"`
	AverageOdometer float64                         `json:"average_odometer"`
	TotalCost       float64                         `json:"total_cost"`
	AverageCost     float64                         `json:"average_cost"`
	ByKind          map[model.ServiceRecordKind]int `json:"by_kind"`
}

// ServiceRecordStats returns totals and breakdowns over every service record.
func (s *Service) ServiceRecordStats() ServiceRecordStats {
	return ServiceRecordStats{
		Count:           s.ServiceRecords.Count(),
		TotalOdometer:   s.ServiceRecords.TotalOdometer(),
		AverageOdometer: s.ServiceRecords.AverageOdometer(),
		TotalCost:       s.ServiceRecords.TotalCost(),
		AverageCost:     s.ServiceRecords.AverageCost(),
		ByKind:          s.ServiceRecords.CountByKind(),
	}
}

// SampleServiceRecord returns valid data for a new service record (links point at seeded records).
func SampleServiceRecord(i int) model.ServiceRecord {
	return model.ServiceRecord{
		VehicleID: (i-1)%3 + 1,
		Serviced:  fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		Odometer:  i + 1,
		Cost:      math.Round((10*float64(i)+0.99)*100) / 100,
		Kind:      model.ServiceRecordKindValues[i%5],
		Notes:     fmt.Sprintf("Notes about service record %d.", i),
	}
}
