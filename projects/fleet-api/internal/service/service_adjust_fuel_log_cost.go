package service

import (
	"fmt"
	"math"

	"fleet-api/internal/model"
)

// AdjustFuelLogCost adds delta to the cost of a fuel log (it can't go below zero).
func (s *Service) AdjustFuelLogCost(id int, delta float64) (model.FuelLog, error) {
	item, err := s.GetFuelLog(id)
	if err != nil {
		return model.FuelLog{}, err
	}
	value := math.Round((item.Cost+delta)*100) / 100
	return s.UpdateFuelLog(id, model.FuelLogPatch{Cost: &value})
}

// FuelLogStats sums up every fuel log.
type FuelLogStats struct {
	Count         int     `json:"count"`
	TotalLitres   float64 `json:"total_litres"`
	AverageLitres float64 `json:"average_litres"`
	TotalCost     float64 `json:"total_cost"`
	AverageCost   float64 `json:"average_cost"`
}

// FuelLogStats returns totals and breakdowns over every fuel log.
func (s *Service) FuelLogStats() FuelLogStats {
	return FuelLogStats{
		Count:         s.FuelLogs.Count(),
		TotalLitres:   s.FuelLogs.TotalLitres(),
		AverageLitres: s.FuelLogs.AverageLitres(),
		TotalCost:     s.FuelLogs.TotalCost(),
		AverageCost:   s.FuelLogs.AverageCost(),
	}
}

// SampleFuelLog returns valid data for a new fuel log (links point at seeded records).
func SampleFuelLog(i int) model.FuelLog {
	return model.FuelLog{
		VehicleID: (i-1)%3 + 1,
		Filled:    fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		Litres:    1.5*float64(i) + 0.25,
		Cost:      math.Round((10*float64(i)+0.99)*100) / 100,
		Station:   fmt.Sprintf("Fuel log station %d", i),
	}
}

// CreateServiceRecord validates and stores a new service record.
func (s *Service) CreateServiceRecord(item model.ServiceRecord) (model.ServiceRecord, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.ServiceRecord{}, err
	}
	if err := s.checkServiceRecordLinks(item); err != nil {
		return model.ServiceRecord{}, err
	}
	return s.ServiceRecords.Create(item), nil
}
