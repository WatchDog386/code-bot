// Package service holds the Fleet Management business rules: validation, links between
// records, small domain operations and statistics.
package service

import (
	"errors"
	"fmt"
	"math"

	"fleet-api/internal/model"
	"fleet-api/internal/store"
)

// Errors the service returns (wrapped with details).
var (
	ErrNotFound = errors.New("not found")
	ErrConflict = errors.New("conflict")
)

func notFound(entity string, id int) error {
	return fmt.Errorf("%s %d: %w", entity, id, ErrNotFound)
}

func inUse(entity string, id, n int, by string) error {
	return fmt.Errorf("%s %d is still used by %d %s: %w", entity, id, n, by, ErrConflict)
}

// Service is the whole application: every store plus the rules between them.
type Service struct {
	Vehicles       *store.VehicleStore
	Drivers        *store.DriverStore
	Trips          *store.TripStore
	FuelLogs       *store.FuelLogStore
	ServiceRecords *store.ServiceRecordStore
	Incidents      *store.IncidentStore
	Documents      *store.DocumentStore
	Notifications  *store.NotificationStore
}

// New returns a service with empty stores.
func New() *Service {
	return &Service{
		Vehicles:       store.NewVehicleStore(),
		Drivers:        store.NewDriverStore(),
		Trips:          store.NewTripStore(),
		FuelLogs:       store.NewFuelLogStore(),
		ServiceRecords: store.NewServiceRecordStore(),
		Incidents:      store.NewIncidentStore(),
		Documents:      store.NewDocumentStore(),
		Notifications:  store.NewNotificationStore(),
	}
}

// Seed creates n sample records of every kind.
func (s *Service) Seed(n int) error {
	for i := 1; i <= n; i++ {
		if _, err := s.CreateVehicle(SampleVehicle(i)); err != nil {
			return err
		}
		if _, err := s.CreateDriver(SampleDriver(i)); err != nil {
			return err
		}
		if _, err := s.CreateTrip(SampleTrip(i)); err != nil {
			return err
		}
		if _, err := s.CreateFuelLog(SampleFuelLog(i)); err != nil {
			return err
		}
		if _, err := s.CreateServiceRecord(SampleServiceRecord(i)); err != nil {
			return err
		}
		if _, err := s.CreateIncident(SampleIncident(i)); err != nil {
			return err
		}
		if _, err := s.CreateDocument(SampleDocument(i)); err != nil {
			return err
		}
		if _, err := s.CreateNotification(SampleNotification(i)); err != nil {
			return err
		}
	}
	return nil
}

// CreateVehicle validates and stores a new vehicle.
func (s *Service) CreateVehicle(item model.Vehicle) (model.Vehicle, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Vehicle{}, err
	}
	if err := s.checkVehicleLinks(item); err != nil {
		return model.Vehicle{}, err
	}
	return s.Vehicles.Create(item), nil
}

// GetVehicle returns one vehicle.
func (s *Service) GetVehicle(id int) (model.Vehicle, error) {
	item, ok := s.Vehicles.Get(id)
	if !ok {
		return model.Vehicle{}, notFound("vehicle", id)
	}
	return item, nil
}

// ListVehicles returns every vehicle, oldest first.
func (s *Service) ListVehicles() []model.Vehicle {
	return s.Vehicles.List()
}

// UpdateVehicle applies patch to a vehicle.
func (s *Service) UpdateVehicle(id int, patch model.VehiclePatch) (model.Vehicle, error) {
	current, err := s.GetVehicle(id)
	if err != nil {
		return model.Vehicle{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Vehicle{}, err
	}
	if err := s.checkVehicleLinks(updated); err != nil {
		return model.Vehicle{}, err
	}
	s.Vehicles.Update(updated)
	return updated, nil
}

// DeleteVehicle removes a vehicle nothing points at any more.
func (s *Service) DeleteVehicle(id int) error {
	if _, err := s.GetVehicle(id); err != nil {
		return err
	}
	if n := s.Trips.CountForVehicle(id); n > 0 {
		return inUse("vehicle", id, n, "trips")
	}
	if n := s.FuelLogs.CountForVehicle(id); n > 0 {
		return inUse("vehicle", id, n, "fuel logs")
	}
	if n := s.ServiceRecords.CountForVehicle(id); n > 0 {
		return inUse("vehicle", id, n, "service records")
	}
	if n := s.Incidents.CountForVehicle(id); n > 0 {
		return inUse("vehicle", id, n, "incidents")
	}
	if n := s.Documents.CountForVehicle(id); n > 0 {
		return inUse("vehicle", id, n, "documents")
	}
	s.Vehicles.Delete(id)
	return nil
}

// checkVehicleLinks makes sure every record a vehicle points at exists.
func (s *Service) checkVehicleLinks(_ model.Vehicle) error {
	return nil
}

// AdjustVehicleYear adds delta to the year of a vehicle (it can't go below zero).
func (s *Service) AdjustVehicleYear(id int, delta int) (model.Vehicle, error) {
	item, err := s.GetVehicle(id)
	if err != nil {
		return model.Vehicle{}, err
	}
	value := item.Year + delta
	return s.UpdateVehicle(id, model.VehiclePatch{Year: &value})
}

// AdjustVehicleMileage adds delta to the mileage of a vehicle (it can't go below zero).
func (s *Service) AdjustVehicleMileage(id int, delta int) (model.Vehicle, error) {
	item, err := s.GetVehicle(id)
	if err != nil {
		return model.Vehicle{}, err
	}
	value := item.Mileage + delta
	return s.UpdateVehicle(id, model.VehiclePatch{Mileage: &value})
}

// SetVehicleFuel moves a vehicle to another fuel.
func (s *Service) SetVehicleFuel(id int, value model.VehicleFuel) (model.Vehicle, error) {
	return s.UpdateVehicle(id, model.VehiclePatch{Fuel: &value})
}

// ToggleVehicleActive flips the active flag of a vehicle.
func (s *Service) ToggleVehicleActive(id int) (model.Vehicle, error) {
	item, err := s.GetVehicle(id)
	if err != nil {
		return model.Vehicle{}, err
	}
	flipped := !item.Active
	return s.UpdateVehicle(id, model.VehiclePatch{Active: &flipped})
}

// VehicleStats sums up every vehicle.
type VehicleStats struct {
	Count          int                       `json:"count"`
	TotalYear      int                       `json:"total_year"`
	AverageYear    float64                   `json:"average_year"`
	TotalMileage   int                       `json:"total_mileage"`
	AverageMileage float64                   `json:"average_mileage"`
	ByFuel         map[model.VehicleFuel]int `json:"by_fuel"`
	Active         int                       `json:"active"`
}

// VehicleStats returns totals and breakdowns over every vehicle.
func (s *Service) VehicleStats() VehicleStats {
	return VehicleStats{
		Count:          s.Vehicles.Count(),
		TotalYear:      s.Vehicles.TotalYear(),
		AverageYear:    s.Vehicles.AverageYear(),
		TotalMileage:   s.Vehicles.TotalMileage(),
		AverageMileage: s.Vehicles.AverageMileage(),
		ByFuel:         s.Vehicles.CountByFuel(),
		Active:         len(s.Vehicles.WhereActive(true)),
	}
}

// SampleVehicle returns valid data for a new vehicle (links point at seeded records).
func SampleVehicle(i int) model.Vehicle {
	return model.Vehicle{
		Plate:   fmt.Sprintf("Vehicle plate %d", i),
		Make:    fmt.Sprintf("Vehicle make %d", i),
		Model:   fmt.Sprintf("Vehicle model %d", i),
		Year:    i + 1,
		Mileage: i + 1,
		Fuel:    model.VehicleFuelValues[i%4],
		Active:  i%2 == 1,
	}
}

// CreateDriver validates and stores a new driver.
func (s *Service) CreateDriver(item model.Driver) (model.Driver, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Driver{}, err
	}
	if err := s.checkDriverLinks(item); err != nil {
		return model.Driver{}, err
	}
	return s.Drivers.Create(item), nil
}

// GetDriver returns one driver.
func (s *Service) GetDriver(id int) (model.Driver, error) {
	item, ok := s.Drivers.Get(id)
	if !ok {
		return model.Driver{}, notFound("driver", id)
	}
	return item, nil
}

// ListDrivers returns every driver, oldest first.
func (s *Service) ListDrivers() []model.Driver {
	return s.Drivers.List()
}

// UpdateDriver applies patch to a driver.
func (s *Service) UpdateDriver(id int, patch model.DriverPatch) (model.Driver, error) {
	current, err := s.GetDriver(id)
	if err != nil {
		return model.Driver{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Driver{}, err
	}
	if err := s.checkDriverLinks(updated); err != nil {
		return model.Driver{}, err
	}
	s.Drivers.Update(updated)
	return updated, nil
}

// DeleteDriver removes a driver nothing points at any more.
func (s *Service) DeleteDriver(id int) error {
	if _, err := s.GetDriver(id); err != nil {
		return err
	}
	if n := s.Trips.CountForDriver(id); n > 0 {
		return inUse("driver", id, n, "trips")
	}
	if n := s.Incidents.CountForDriver(id); n > 0 {
		return inUse("driver", id, n, "incidents")
	}
	s.Drivers.Delete(id)
	return nil
}

// checkDriverLinks makes sure every record a driver points at exists.
func (s *Service) checkDriverLinks(_ model.Driver) error {
	return nil
}

// AdjustDriverRating adds delta to the rating of a driver (it can't go below zero).
func (s *Service) AdjustDriverRating(id int, delta float64) (model.Driver, error) {
	item, err := s.GetDriver(id)
	if err != nil {
		return model.Driver{}, err
	}
	value := math.Round((item.Rating+delta)*100) / 100
	return s.UpdateDriver(id, model.DriverPatch{Rating: &value})
}

// ToggleDriverOnDuty flips the on duty flag of a driver.
func (s *Service) ToggleDriverOnDuty(id int) (model.Driver, error) {
	item, err := s.GetDriver(id)
	if err != nil {
		return model.Driver{}, err
	}
	flipped := !item.OnDuty
	return s.UpdateDriver(id, model.DriverPatch{OnDuty: &flipped})
}

// DriverStats sums up every driver.
type DriverStats struct {
	Count         int     `json:"count"`
	TotalRating   float64 `json:"total_rating"`
	AverageRating float64 `json:"average_rating"`
	OnDuty        int     `json:"on_duty"`
}

// DriverStats returns totals and breakdowns over every driver.
func (s *Service) DriverStats() DriverStats {
	return DriverStats{
		Count:         s.Drivers.Count(),
		TotalRating:   s.Drivers.TotalRating(),
		AverageRating: s.Drivers.AverageRating(),
		OnDuty:        len(s.Drivers.WhereOnDuty(true)),
	}
}

// SampleDriver returns valid data for a new driver (links point at seeded records).
func SampleDriver(i int) model.Driver {
	return model.Driver{
		Name:          fmt.Sprintf("Driver name %d", i),
		Email:         fmt.Sprintf("driver%d@example.com", i),
		LicenseNo:     fmt.Sprintf("Driver license no %d", i),
		LicenseExpiry: fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		Rating:        1.5*float64(i) + 0.25,
		OnDuty:        i%2 == 1,
	}
}

// CreateTrip validates and stores a new trip.
func (s *Service) CreateTrip(item model.Trip) (model.Trip, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Trip{}, err
	}
	if err := s.checkTripLinks(item); err != nil {
		return model.Trip{}, err
	}
	return s.Trips.Create(item), nil
}

// GetTrip returns one trip.
func (s *Service) GetTrip(id int) (model.Trip, error) {
	item, ok := s.Trips.Get(id)
	if !ok {
		return model.Trip{}, notFound("trip", id)
	}
	return item, nil
}

// ListTrips returns every trip, oldest first.
func (s *Service) ListTrips() []model.Trip {
	return s.Trips.List()
}

// UpdateTrip applies patch to a trip.
func (s *Service) UpdateTrip(id int, patch model.TripPatch) (model.Trip, error) {
	current, err := s.GetTrip(id)
	if err != nil {
		return model.Trip{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Trip{}, err
	}
	if err := s.checkTripLinks(updated); err != nil {
		return model.Trip{}, err
	}
	s.Trips.Update(updated)
	return updated, nil
}

// DeleteTrip removes a trip nothing points at any more.
func (s *Service) DeleteTrip(id int) error {
	if _, err := s.GetTrip(id); err != nil {
		return err
	}
	s.Trips.Delete(id)
	return nil
}

// checkTripLinks makes sure every record a trip points at exists.
func (s *Service) checkTripLinks(item model.Trip) error {
	if _, ok := s.Vehicles.Get(item.VehicleID); !ok {
		return notFound("vehicle", item.VehicleID)
	}
	if _, ok := s.Drivers.Get(item.DriverID); !ok {
		return notFound("driver", item.DriverID)
	}
	return nil
}

// AdjustTripDistanceKm adds delta to the distance km of a trip (it can't go below zero).
func (s *Service) AdjustTripDistanceKm(id int, delta float64) (model.Trip, error) {
	item, err := s.GetTrip(id)
	if err != nil {
		return model.Trip{}, err
	}
	value := math.Round((item.DistanceKm+delta)*100) / 100
	return s.UpdateTrip(id, model.TripPatch{DistanceKm: &value})
}

// SetTripStatus moves a trip to another status.
func (s *Service) SetTripStatus(id int, value model.TripStatus) (model.Trip, error) {
	return s.UpdateTrip(id, model.TripPatch{Status: &value})
}

// TripStats sums up every trip.
type TripStats struct {
	Count             int                      `json:"count"`
	TotalDistanceKm   float64                  `json:"total_distance_km"`
	AverageDistanceKm float64                  `json:"average_distance_km"`
	ByStatus          map[model.TripStatus]int `json:"by_status"`
}

// TripStats returns totals and breakdowns over every trip.
func (s *Service) TripStats() TripStats {
	return TripStats{
		Count:             s.Trips.Count(),
		TotalDistanceKm:   s.Trips.TotalDistanceKm(),
		AverageDistanceKm: s.Trips.AverageDistanceKm(),
		ByStatus:          s.Trips.CountByStatus(),
	}
}

// SampleTrip returns valid data for a new trip (links point at seeded records).
func SampleTrip(i int) model.Trip {
	return model.Trip{
		VehicleID:  (i-1)%3 + 1,
		DriverID:   (i-1)%3 + 1,
		Started:    fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		DistanceKm: 1.5*float64(i) + 0.25,
		Purpose:    fmt.Sprintf("Trip purpose %d", i),
		Status:     model.TripStatusValues[i%4],
	}
}

// CreateFuelLog validates and stores a new fuel log.
func (s *Service) CreateFuelLog(item model.FuelLog) (model.FuelLog, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.FuelLog{}, err
	}
	if err := s.checkFuelLogLinks(item); err != nil {
		return model.FuelLog{}, err
	}
	return s.FuelLogs.Create(item), nil
}

// GetFuelLog returns one fuel log.
func (s *Service) GetFuelLog(id int) (model.FuelLog, error) {
	item, ok := s.FuelLogs.Get(id)
	if !ok {
		return model.FuelLog{}, notFound("fuel log", id)
	}
	return item, nil
}

// ListFuelLogs returns every fuel log, oldest first.
func (s *Service) ListFuelLogs() []model.FuelLog {
	return s.FuelLogs.List()
}

// UpdateFuelLog applies patch to a fuel log.
func (s *Service) UpdateFuelLog(id int, patch model.FuelLogPatch) (model.FuelLog, error) {
	current, err := s.GetFuelLog(id)
	if err != nil {
		return model.FuelLog{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.FuelLog{}, err
	}
	if err := s.checkFuelLogLinks(updated); err != nil {
		return model.FuelLog{}, err
	}
	s.FuelLogs.Update(updated)
	return updated, nil
}

// DeleteFuelLog removes a fuel log nothing points at any more.
func (s *Service) DeleteFuelLog(id int) error {
	if _, err := s.GetFuelLog(id); err != nil {
		return err
	}
	s.FuelLogs.Delete(id)
	return nil
}

// checkFuelLogLinks makes sure every record a fuel log points at exists.
func (s *Service) checkFuelLogLinks(item model.FuelLog) error {
	if _, ok := s.Vehicles.Get(item.VehicleID); !ok {
		return notFound("vehicle", item.VehicleID)
	}
	return nil
}

// AdjustFuelLogLitres adds delta to the litres of a fuel log (it can't go below zero).
func (s *Service) AdjustFuelLogLitres(id int, delta float64) (model.FuelLog, error) {
	item, err := s.GetFuelLog(id)
	if err != nil {
		return model.FuelLog{}, err
	}
	value := math.Round((item.Litres+delta)*100) / 100
	return s.UpdateFuelLog(id, model.FuelLogPatch{Litres: &value})
}

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

// GetServiceRecord returns one service record.
func (s *Service) GetServiceRecord(id int) (model.ServiceRecord, error) {
	item, ok := s.ServiceRecords.Get(id)
	if !ok {
		return model.ServiceRecord{}, notFound("service record", id)
	}
	return item, nil
}

// ListServiceRecords returns every service record, oldest first.
func (s *Service) ListServiceRecords() []model.ServiceRecord {
	return s.ServiceRecords.List()
}

// UpdateServiceRecord applies patch to a service record.
func (s *Service) UpdateServiceRecord(id int, patch model.ServiceRecordPatch) (model.ServiceRecord, error) {
	current, err := s.GetServiceRecord(id)
	if err != nil {
		return model.ServiceRecord{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.ServiceRecord{}, err
	}
	if err := s.checkServiceRecordLinks(updated); err != nil {
		return model.ServiceRecord{}, err
	}
	s.ServiceRecords.Update(updated)
	return updated, nil
}

// DeleteServiceRecord removes a service record nothing points at any more.
func (s *Service) DeleteServiceRecord(id int) error {
	if _, err := s.GetServiceRecord(id); err != nil {
		return err
	}
	s.ServiceRecords.Delete(id)
	return nil
}

// checkServiceRecordLinks makes sure every record a service record points at exists.
func (s *Service) checkServiceRecordLinks(item model.ServiceRecord) error {
	if _, ok := s.Vehicles.Get(item.VehicleID); !ok {
		return notFound("vehicle", item.VehicleID)
	}
	return nil
}

// AdjustServiceRecordOdometer adds delta to the odometer of a service record (it can't go below zero).
func (s *Service) AdjustServiceRecordOdometer(id int, delta int) (model.ServiceRecord, error) {
	item, err := s.GetServiceRecord(id)
	if err != nil {
		return model.ServiceRecord{}, err
	}
	value := item.Odometer + delta
	return s.UpdateServiceRecord(id, model.ServiceRecordPatch{Odometer: &value})
}

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

// CreateIncident validates and stores a new incident.
func (s *Service) CreateIncident(item model.Incident) (model.Incident, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Incident{}, err
	}
	if err := s.checkIncidentLinks(item); err != nil {
		return model.Incident{}, err
	}
	return s.Incidents.Create(item), nil
}

// GetIncident returns one incident.
func (s *Service) GetIncident(id int) (model.Incident, error) {
	item, ok := s.Incidents.Get(id)
	if !ok {
		return model.Incident{}, notFound("incident", id)
	}
	return item, nil
}

// ListIncidents returns every incident, oldest first.
func (s *Service) ListIncidents() []model.Incident {
	return s.Incidents.List()
}

// UpdateIncident applies patch to a incident.
func (s *Service) UpdateIncident(id int, patch model.IncidentPatch) (model.Incident, error) {
	current, err := s.GetIncident(id)
	if err != nil {
		return model.Incident{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Incident{}, err
	}
	if err := s.checkIncidentLinks(updated); err != nil {
		return model.Incident{}, err
	}
	s.Incidents.Update(updated)
	return updated, nil
}

// DeleteIncident removes a incident nothing points at any more.
func (s *Service) DeleteIncident(id int) error {
	if _, err := s.GetIncident(id); err != nil {
		return err
	}
	s.Incidents.Delete(id)
	return nil
}

// checkIncidentLinks makes sure every record a incident points at exists.
func (s *Service) checkIncidentLinks(item model.Incident) error {
	if _, ok := s.Vehicles.Get(item.VehicleID); !ok {
		return notFound("vehicle", item.VehicleID)
	}
	if _, ok := s.Drivers.Get(item.DriverID); !ok {
		return notFound("driver", item.DriverID)
	}
	return nil
}

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

// CreateDocument validates and stores a new document.
func (s *Service) CreateDocument(item model.Document) (model.Document, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Document{}, err
	}
	if err := s.checkDocumentLinks(item); err != nil {
		return model.Document{}, err
	}
	return s.Documents.Create(item), nil
}

// GetDocument returns one document.
func (s *Service) GetDocument(id int) (model.Document, error) {
	item, ok := s.Documents.Get(id)
	if !ok {
		return model.Document{}, notFound("document", id)
	}
	return item, nil
}

// ListDocuments returns every document, oldest first.
func (s *Service) ListDocuments() []model.Document {
	return s.Documents.List()
}

// UpdateDocument applies patch to a document.
func (s *Service) UpdateDocument(id int, patch model.DocumentPatch) (model.Document, error) {
	current, err := s.GetDocument(id)
	if err != nil {
		return model.Document{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Document{}, err
	}
	if err := s.checkDocumentLinks(updated); err != nil {
		return model.Document{}, err
	}
	s.Documents.Update(updated)
	return updated, nil
}

// DeleteDocument removes a document nothing points at any more.
func (s *Service) DeleteDocument(id int) error {
	if _, err := s.GetDocument(id); err != nil {
		return err
	}
	s.Documents.Delete(id)
	return nil
}

// checkDocumentLinks makes sure every record a document points at exists.
func (s *Service) checkDocumentLinks(item model.Document) error {
	if _, ok := s.Vehicles.Get(item.VehicleID); !ok {
		return notFound("vehicle", item.VehicleID)
	}
	return nil
}

// AdjustDocumentPages adds delta to the pages of a document (it can't go below zero).
func (s *Service) AdjustDocumentPages(id int, delta int) (model.Document, error) {
	item, err := s.GetDocument(id)
	if err != nil {
		return model.Document{}, err
	}
	value := item.Pages + delta
	return s.UpdateDocument(id, model.DocumentPatch{Pages: &value})
}

// ToggleDocumentSigned flips the signed flag of a document.
func (s *Service) ToggleDocumentSigned(id int) (model.Document, error) {
	item, err := s.GetDocument(id)
	if err != nil {
		return model.Document{}, err
	}
	flipped := !item.Signed
	return s.UpdateDocument(id, model.DocumentPatch{Signed: &flipped})
}

// AdjustDocumentVersion adds delta to the version of a document (it can't go below zero).
func (s *Service) AdjustDocumentVersion(id int, delta int) (model.Document, error) {
	item, err := s.GetDocument(id)
	if err != nil {
		return model.Document{}, err
	}
	value := item.Version + delta
	return s.UpdateDocument(id, model.DocumentPatch{Version: &value})
}

// DocumentStats sums up every document.
type DocumentStats struct {
	Count          int     `json:"count"`
	TotalPages     int     `json:"total_pages"`
	AveragePages   float64 `json:"average_pages"`
	Signed         int     `json:"signed"`
	TotalVersion   int     `json:"total_version"`
	AverageVersion float64 `json:"average_version"`
}

// DocumentStats returns totals and breakdowns over every document.
func (s *Service) DocumentStats() DocumentStats {
	return DocumentStats{
		Count:          s.Documents.Count(),
		TotalPages:     s.Documents.TotalPages(),
		AveragePages:   s.Documents.AveragePages(),
		Signed:         len(s.Documents.WhereSigned(true)),
		TotalVersion:   s.Documents.TotalVersion(),
		AverageVersion: s.Documents.AverageVersion(),
	}
}

// SampleDocument returns valid data for a new document (links point at seeded records).
func SampleDocument(i int) model.Document {
	return model.Document{
		VehicleID: (i-1)%3 + 1,
		Title:     fmt.Sprintf("Document title %d", i),
		Pages:     i + 1,
		Signed:    i%2 == 1,
		Version:   i + 1,
		Issued:    fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
	}
}

// CreateNotification validates and stores a new notification.
func (s *Service) CreateNotification(item model.Notification) (model.Notification, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Notification{}, err
	}
	if err := s.checkNotificationLinks(item); err != nil {
		return model.Notification{}, err
	}
	return s.Notifications.Create(item), nil
}

// GetNotification returns one notification.
func (s *Service) GetNotification(id int) (model.Notification, error) {
	item, ok := s.Notifications.Get(id)
	if !ok {
		return model.Notification{}, notFound("notification", id)
	}
	return item, nil
}

// ListNotifications returns every notification, oldest first.
func (s *Service) ListNotifications() []model.Notification {
	return s.Notifications.List()
}

// UpdateNotification applies patch to a notification.
func (s *Service) UpdateNotification(id int, patch model.NotificationPatch) (model.Notification, error) {
	current, err := s.GetNotification(id)
	if err != nil {
		return model.Notification{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Notification{}, err
	}
	if err := s.checkNotificationLinks(updated); err != nil {
		return model.Notification{}, err
	}
	s.Notifications.Update(updated)
	return updated, nil
}

// DeleteNotification removes a notification nothing points at any more.
func (s *Service) DeleteNotification(id int) error {
	if _, err := s.GetNotification(id); err != nil {
		return err
	}
	s.Notifications.Delete(id)
	return nil
}

// checkNotificationLinks makes sure every record a notification points at exists.
func (s *Service) checkNotificationLinks(_ model.Notification) error {
	return nil
}

// SetNotificationChannel moves a notification to another channel.
func (s *Service) SetNotificationChannel(id int, value model.NotificationChannel) (model.Notification, error) {
	return s.UpdateNotification(id, model.NotificationPatch{Channel: &value})
}

// ToggleNotificationRead flips the read flag of a notification.
func (s *Service) ToggleNotificationRead(id int) (model.Notification, error) {
	item, err := s.GetNotification(id)
	if err != nil {
		return model.Notification{}, err
	}
	flipped := !item.Read
	return s.UpdateNotification(id, model.NotificationPatch{Read: &flipped})
}

// NotificationStats sums up every notification.
type NotificationStats struct {
	Count     int                               `json:"count"`
	ByChannel map[model.NotificationChannel]int `json:"by_channel"`
	Read      int                               `json:"read"`
}

// NotificationStats returns totals and breakdowns over every notification.
func (s *Service) NotificationStats() NotificationStats {
	return NotificationStats{
		Count:     s.Notifications.Count(),
		ByChannel: s.Notifications.CountByChannel(),
		Read:      len(s.Notifications.WhereRead(true)),
	}
}

// SampleNotification returns valid data for a new notification (links point at seeded records).
func SampleNotification(i int) model.Notification {
	return model.Notification{
		Recipient: fmt.Sprintf("notification%d@example.com", i),
		Title:     fmt.Sprintf("Notification title %d", i),
		Sent:      fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		Channel:   model.NotificationChannelValues[i%3],
		Read:      i%2 == 1,
	}
}
