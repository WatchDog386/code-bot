// Package store keeps the Fleet Management records in memory, safe for concurrent use.
package store

import (
	"sort"
	"strings"
	"sync"

	"fleet-api/internal/model"
)

// VehicleStore keeps every vehicle.
type VehicleStore struct {
	mu     sync.RWMutex
	items  map[int]model.Vehicle
	nextID int
}

// NewVehicleStore returns an empty store.
func NewVehicleStore() *VehicleStore {
	return &VehicleStore{items: map[int]model.Vehicle{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *VehicleStore) Create(item model.Vehicle) model.Vehicle {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *VehicleStore) Get(id int) (model.Vehicle, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *VehicleStore) List() []model.Vehicle {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.Vehicle, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *VehicleStore) Update(item model.Vehicle) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *VehicleStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *VehicleStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *VehicleStore) Filter(keep func(model.Vehicle) bool) []model.Vehicle {
	out := []model.Vehicle{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// FindByPlate returns records whose plate is exactly value.
func (s *VehicleStore) FindByPlate(value string) []model.Vehicle {
	return s.Filter(func(item model.Vehicle) bool { return item.Plate == value })
}

// SearchPlate returns records whose plate contains text (any case).
func (s *VehicleStore) SearchPlate(text string) []model.Vehicle {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Vehicle) bool { return strings.Contains(strings.ToLower(item.Plate), needle) })
}

// FindByMake returns records whose make is exactly value.
func (s *VehicleStore) FindByMake(value string) []model.Vehicle {
	return s.Filter(func(item model.Vehicle) bool { return item.Make == value })
}

// SearchMake returns records whose make contains text (any case).
func (s *VehicleStore) SearchMake(text string) []model.Vehicle {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Vehicle) bool { return strings.Contains(strings.ToLower(item.Make), needle) })
}

// FindByModel returns records whose model is exactly value.
func (s *VehicleStore) FindByModel(value string) []model.Vehicle {
	return s.Filter(func(item model.Vehicle) bool { return item.Model == value })
}

// SearchModel returns records whose model contains text (any case).
func (s *VehicleStore) SearchModel(text string) []model.Vehicle {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Vehicle) bool { return strings.Contains(strings.ToLower(item.Model), needle) })
}

// BetweenYear returns records whose year is within [low, high].
func (s *VehicleStore) BetweenYear(low, high int) []model.Vehicle {
	return s.Filter(func(item model.Vehicle) bool { return item.Year >= low && item.Year <= high })
}

// TotalYear adds up the year of every record.
func (s *VehicleStore) TotalYear() int {
	var total int
	for _, item := range s.List() {
		total += item.Year
	}
	return total
}

// AverageYear is the mean year (0 when there are no records).
func (s *VehicleStore) AverageYear() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalYear()) / float64(len(items))
}

// MaxYear returns the record with the highest year.
func (s *VehicleStore) MaxYear() (model.Vehicle, bool) {
	var best model.Vehicle
	found := false
	for _, item := range s.List() {
		if !found || item.Year > best.Year {
			best, found = item, true
		}
	}
	return best, found
}

// BetweenMileage returns records whose mileage is within [low, high].
func (s *VehicleStore) BetweenMileage(low, high int) []model.Vehicle {
	return s.Filter(func(item model.Vehicle) bool { return item.Mileage >= low && item.Mileage <= high })
}

// TotalMileage adds up the mileage of every record.
func (s *VehicleStore) TotalMileage() int {
	var total int
	for _, item := range s.List() {
		total += item.Mileage
	}
	return total
}

// AverageMileage is the mean mileage (0 when there are no records).
func (s *VehicleStore) AverageMileage() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalMileage()) / float64(len(items))
}

// MaxMileage returns the record with the highest mileage.
func (s *VehicleStore) MaxMileage() (model.Vehicle, bool) {
	var best model.Vehicle
	found := false
	for _, item := range s.List() {
		if !found || item.Mileage > best.Mileage {
			best, found = item, true
		}
	}
	return best, found
}

// WithFuel returns records whose fuel is value.
func (s *VehicleStore) WithFuel(value model.VehicleFuel) []model.Vehicle {
	return s.Filter(func(item model.Vehicle) bool { return item.Fuel == value })
}

// CountByFuel counts records for every fuel.
func (s *VehicleStore) CountByFuel() map[model.VehicleFuel]int {
	counts := map[model.VehicleFuel]int{}
	for _, v := range model.VehicleFuelValues {
		counts[v] = 0
	}
	for _, item := range s.List() {
		counts[item.Fuel]++
	}
	return counts
}

// WhereActive returns records whose active flag equals flag.
func (s *VehicleStore) WhereActive(flag bool) []model.Vehicle {
	return s.Filter(func(item model.Vehicle) bool { return item.Active == flag })
}

// Search returns records where any text field contains text (any case).
func (s *VehicleStore) Search(text string) []model.Vehicle {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Vehicle) bool {
		for _, value := range []string{item.Plate, item.Make, item.Model} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// DriverStore keeps every driver.
type DriverStore struct {
	mu     sync.RWMutex
	items  map[int]model.Driver
	nextID int
}

// NewDriverStore returns an empty store.
func NewDriverStore() *DriverStore {
	return &DriverStore{items: map[int]model.Driver{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *DriverStore) Create(item model.Driver) model.Driver {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *DriverStore) Get(id int) (model.Driver, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *DriverStore) List() []model.Driver {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.Driver, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *DriverStore) Update(item model.Driver) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *DriverStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *DriverStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *DriverStore) Filter(keep func(model.Driver) bool) []model.Driver {
	out := []model.Driver{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// FindByName returns records whose name is exactly value.
func (s *DriverStore) FindByName(value string) []model.Driver {
	return s.Filter(func(item model.Driver) bool { return item.Name == value })
}

// SearchName returns records whose name contains text (any case).
func (s *DriverStore) SearchName(text string) []model.Driver {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Driver) bool { return strings.Contains(strings.ToLower(item.Name), needle) })
}

// FindByEmail returns records whose email is exactly value.
func (s *DriverStore) FindByEmail(value string) []model.Driver {
	return s.Filter(func(item model.Driver) bool { return item.Email == value })
}

// SearchEmail returns records whose email contains text (any case).
func (s *DriverStore) SearchEmail(text string) []model.Driver {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Driver) bool { return strings.Contains(strings.ToLower(item.Email), needle) })
}

// FindByLicenseNo returns records whose license no is exactly value.
func (s *DriverStore) FindByLicenseNo(value string) []model.Driver {
	return s.Filter(func(item model.Driver) bool { return item.LicenseNo == value })
}

// SearchLicenseNo returns records whose license no contains text (any case).
func (s *DriverStore) SearchLicenseNo(text string) []model.Driver {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Driver) bool { return strings.Contains(strings.ToLower(item.LicenseNo), needle) })
}

// LicenseExpiryBefore returns records whose license expiry is before day (YYYY-MM-DD).
func (s *DriverStore) LicenseExpiryBefore(day string) []model.Driver {
	return s.Filter(func(item model.Driver) bool { return item.LicenseExpiry < day })
}

// LicenseExpiryAfter returns records whose license expiry is after day (YYYY-MM-DD).
func (s *DriverStore) LicenseExpiryAfter(day string) []model.Driver {
	return s.Filter(func(item model.Driver) bool { return item.LicenseExpiry > day })
}

// LicenseExpiryOn returns records whose license expiry is day.
func (s *DriverStore) LicenseExpiryOn(day string) []model.Driver {
	return s.Filter(func(item model.Driver) bool { return item.LicenseExpiry == day })
}

// BetweenRating returns records whose rating is within [low, high].
func (s *DriverStore) BetweenRating(low, high float64) []model.Driver {
	return s.Filter(func(item model.Driver) bool { return item.Rating >= low && item.Rating <= high })
}

// TotalRating adds up the rating of every record.
func (s *DriverStore) TotalRating() float64 {
	var total float64
	for _, item := range s.List() {
		total += item.Rating
	}
	return total
}

// AverageRating is the mean rating (0 when there are no records).
func (s *DriverStore) AverageRating() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalRating()) / float64(len(items))
}

// MaxRating returns the record with the highest rating.
func (s *DriverStore) MaxRating() (model.Driver, bool) {
	var best model.Driver
	found := false
	for _, item := range s.List() {
		if !found || item.Rating > best.Rating {
			best, found = item, true
		}
	}
	return best, found
}

// WhereOnDuty returns records whose on duty flag equals flag.
func (s *DriverStore) WhereOnDuty(flag bool) []model.Driver {
	return s.Filter(func(item model.Driver) bool { return item.OnDuty == flag })
}

// Search returns records where any text field contains text (any case).
func (s *DriverStore) Search(text string) []model.Driver {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Driver) bool {
		for _, value := range []string{item.Name, item.Email, item.LicenseNo} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// TripStore keeps every trip.
type TripStore struct {
	mu     sync.RWMutex
	items  map[int]model.Trip
	nextID int
}

// NewTripStore returns an empty store.
func NewTripStore() *TripStore {
	return &TripStore{items: map[int]model.Trip{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *TripStore) Create(item model.Trip) model.Trip {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *TripStore) Get(id int) (model.Trip, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *TripStore) List() []model.Trip {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.Trip, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *TripStore) Update(item model.Trip) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *TripStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *TripStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *TripStore) Filter(keep func(model.Trip) bool) []model.Trip {
	out := []model.Trip{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// ForVehicle returns records linked to vehicle id.
func (s *TripStore) ForVehicle(id int) []model.Trip {
	return s.Filter(func(item model.Trip) bool { return item.VehicleID == id })
}

// CountForVehicle counts records linked to vehicle id.
func (s *TripStore) CountForVehicle(id int) int {
	return len(s.ForVehicle(id))
}

// ForDriver returns records linked to driver id.
func (s *TripStore) ForDriver(id int) []model.Trip {
	return s.Filter(func(item model.Trip) bool { return item.DriverID == id })
}

// CountForDriver counts records linked to driver id.
func (s *TripStore) CountForDriver(id int) int {
	return len(s.ForDriver(id))
}

// StartedBefore returns records whose started is before day (YYYY-MM-DD).
func (s *TripStore) StartedBefore(day string) []model.Trip {
	return s.Filter(func(item model.Trip) bool { return item.Started < day })
}

// StartedAfter returns records whose started is after day (YYYY-MM-DD).
func (s *TripStore) StartedAfter(day string) []model.Trip {
	return s.Filter(func(item model.Trip) bool { return item.Started > day })
}

// StartedOn returns records whose started is day.
func (s *TripStore) StartedOn(day string) []model.Trip {
	return s.Filter(func(item model.Trip) bool { return item.Started == day })
}

// BetweenDistanceKm returns records whose distance km is within [low, high].
func (s *TripStore) BetweenDistanceKm(low, high float64) []model.Trip {
	return s.Filter(func(item model.Trip) bool { return item.DistanceKm >= low && item.DistanceKm <= high })
}

// TotalDistanceKm adds up the distance km of every record.
func (s *TripStore) TotalDistanceKm() float64 {
	var total float64
	for _, item := range s.List() {
		total += item.DistanceKm
	}
	return total
}

// AverageDistanceKm is the mean distance km (0 when there are no records).
func (s *TripStore) AverageDistanceKm() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalDistanceKm()) / float64(len(items))
}

// MaxDistanceKm returns the record with the highest distance km.
func (s *TripStore) MaxDistanceKm() (model.Trip, bool) {
	var best model.Trip
	found := false
	for _, item := range s.List() {
		if !found || item.DistanceKm > best.DistanceKm {
			best, found = item, true
		}
	}
	return best, found
}

// FindByPurpose returns records whose purpose is exactly value.
func (s *TripStore) FindByPurpose(value string) []model.Trip {
	return s.Filter(func(item model.Trip) bool { return item.Purpose == value })
}

// SearchPurpose returns records whose purpose contains text (any case).
func (s *TripStore) SearchPurpose(text string) []model.Trip {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Trip) bool { return strings.Contains(strings.ToLower(item.Purpose), needle) })
}

// WithStatus returns records whose status is value.
func (s *TripStore) WithStatus(value model.TripStatus) []model.Trip {
	return s.Filter(func(item model.Trip) bool { return item.Status == value })
}

// CountByStatus counts records for every status.
func (s *TripStore) CountByStatus() map[model.TripStatus]int {
	counts := map[model.TripStatus]int{}
	for _, v := range model.TripStatusValues {
		counts[v] = 0
	}
	for _, item := range s.List() {
		counts[item.Status]++
	}
	return counts
}

// Search returns records where any text field contains text (any case).
func (s *TripStore) Search(text string) []model.Trip {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Trip) bool {
		for _, value := range []string{item.Purpose} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// FuelLogStore keeps every fuel log.
type FuelLogStore struct {
	mu     sync.RWMutex
	items  map[int]model.FuelLog
	nextID int
}

// NewFuelLogStore returns an empty store.
func NewFuelLogStore() *FuelLogStore {
	return &FuelLogStore{items: map[int]model.FuelLog{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *FuelLogStore) Create(item model.FuelLog) model.FuelLog {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *FuelLogStore) Get(id int) (model.FuelLog, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *FuelLogStore) List() []model.FuelLog {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.FuelLog, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *FuelLogStore) Update(item model.FuelLog) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *FuelLogStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *FuelLogStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *FuelLogStore) Filter(keep func(model.FuelLog) bool) []model.FuelLog {
	out := []model.FuelLog{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// ForVehicle returns records linked to vehicle id.
func (s *FuelLogStore) ForVehicle(id int) []model.FuelLog {
	return s.Filter(func(item model.FuelLog) bool { return item.VehicleID == id })
}

// CountForVehicle counts records linked to vehicle id.
func (s *FuelLogStore) CountForVehicle(id int) int {
	return len(s.ForVehicle(id))
}

// FilledBefore returns records whose filled is before day (YYYY-MM-DD).
func (s *FuelLogStore) FilledBefore(day string) []model.FuelLog {
	return s.Filter(func(item model.FuelLog) bool { return item.Filled < day })
}

// FilledAfter returns records whose filled is after day (YYYY-MM-DD).
func (s *FuelLogStore) FilledAfter(day string) []model.FuelLog {
	return s.Filter(func(item model.FuelLog) bool { return item.Filled > day })
}

// FilledOn returns records whose filled is day.
func (s *FuelLogStore) FilledOn(day string) []model.FuelLog {
	return s.Filter(func(item model.FuelLog) bool { return item.Filled == day })
}

// BetweenLitres returns records whose litres is within [low, high].
func (s *FuelLogStore) BetweenLitres(low, high float64) []model.FuelLog {
	return s.Filter(func(item model.FuelLog) bool { return item.Litres >= low && item.Litres <= high })
}

// TotalLitres adds up the litres of every record.
func (s *FuelLogStore) TotalLitres() float64 {
	var total float64
	for _, item := range s.List() {
		total += item.Litres
	}
	return total
}

// AverageLitres is the mean litres (0 when there are no records).
func (s *FuelLogStore) AverageLitres() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalLitres()) / float64(len(items))
}

// MaxLitres returns the record with the highest litres.
func (s *FuelLogStore) MaxLitres() (model.FuelLog, bool) {
	var best model.FuelLog
	found := false
	for _, item := range s.List() {
		if !found || item.Litres > best.Litres {
			best, found = item, true
		}
	}
	return best, found
}

// BetweenCost returns records whose cost is within [low, high].
func (s *FuelLogStore) BetweenCost(low, high float64) []model.FuelLog {
	return s.Filter(func(item model.FuelLog) bool { return item.Cost >= low && item.Cost <= high })
}

// TotalCost adds up the cost of every record.
func (s *FuelLogStore) TotalCost() float64 {
	var total float64
	for _, item := range s.List() {
		total += item.Cost
	}
	return total
}

// AverageCost is the mean cost (0 when there are no records).
func (s *FuelLogStore) AverageCost() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalCost()) / float64(len(items))
}

// MaxCost returns the record with the highest cost.
func (s *FuelLogStore) MaxCost() (model.FuelLog, bool) {
	var best model.FuelLog
	found := false
	for _, item := range s.List() {
		if !found || item.Cost > best.Cost {
			best, found = item, true
		}
	}
	return best, found
}

// FindByStation returns records whose station is exactly value.
func (s *FuelLogStore) FindByStation(value string) []model.FuelLog {
	return s.Filter(func(item model.FuelLog) bool { return item.Station == value })
}

// SearchStation returns records whose station contains text (any case).
func (s *FuelLogStore) SearchStation(text string) []model.FuelLog {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.FuelLog) bool { return strings.Contains(strings.ToLower(item.Station), needle) })
}

// Search returns records where any text field contains text (any case).
func (s *FuelLogStore) Search(text string) []model.FuelLog {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.FuelLog) bool {
		for _, value := range []string{item.Station} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// ServiceRecordStore keeps every service record.
type ServiceRecordStore struct {
	mu     sync.RWMutex
	items  map[int]model.ServiceRecord
	nextID int
}

// NewServiceRecordStore returns an empty store.
func NewServiceRecordStore() *ServiceRecordStore {
	return &ServiceRecordStore{items: map[int]model.ServiceRecord{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *ServiceRecordStore) Create(item model.ServiceRecord) model.ServiceRecord {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *ServiceRecordStore) Get(id int) (model.ServiceRecord, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *ServiceRecordStore) List() []model.ServiceRecord {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.ServiceRecord, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *ServiceRecordStore) Update(item model.ServiceRecord) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *ServiceRecordStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *ServiceRecordStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *ServiceRecordStore) Filter(keep func(model.ServiceRecord) bool) []model.ServiceRecord {
	out := []model.ServiceRecord{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// ForVehicle returns records linked to vehicle id.
func (s *ServiceRecordStore) ForVehicle(id int) []model.ServiceRecord {
	return s.Filter(func(item model.ServiceRecord) bool { return item.VehicleID == id })
}

// CountForVehicle counts records linked to vehicle id.
func (s *ServiceRecordStore) CountForVehicle(id int) int {
	return len(s.ForVehicle(id))
}

// ServicedBefore returns records whose serviced is before day (YYYY-MM-DD).
func (s *ServiceRecordStore) ServicedBefore(day string) []model.ServiceRecord {
	return s.Filter(func(item model.ServiceRecord) bool { return item.Serviced < day })
}

// ServicedAfter returns records whose serviced is after day (YYYY-MM-DD).
func (s *ServiceRecordStore) ServicedAfter(day string) []model.ServiceRecord {
	return s.Filter(func(item model.ServiceRecord) bool { return item.Serviced > day })
}

// ServicedOn returns records whose serviced is day.
func (s *ServiceRecordStore) ServicedOn(day string) []model.ServiceRecord {
	return s.Filter(func(item model.ServiceRecord) bool { return item.Serviced == day })
}

// BetweenOdometer returns records whose odometer is within [low, high].
func (s *ServiceRecordStore) BetweenOdometer(low, high int) []model.ServiceRecord {
	return s.Filter(func(item model.ServiceRecord) bool { return item.Odometer >= low && item.Odometer <= high })
}

// TotalOdometer adds up the odometer of every record.
func (s *ServiceRecordStore) TotalOdometer() int {
	var total int
	for _, item := range s.List() {
		total += item.Odometer
	}
	return total
}

// AverageOdometer is the mean odometer (0 when there are no records).
func (s *ServiceRecordStore) AverageOdometer() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalOdometer()) / float64(len(items))
}

// MaxOdometer returns the record with the highest odometer.
func (s *ServiceRecordStore) MaxOdometer() (model.ServiceRecord, bool) {
	var best model.ServiceRecord
	found := false
	for _, item := range s.List() {
		if !found || item.Odometer > best.Odometer {
			best, found = item, true
		}
	}
	return best, found
}

// BetweenCost returns records whose cost is within [low, high].
func (s *ServiceRecordStore) BetweenCost(low, high float64) []model.ServiceRecord {
	return s.Filter(func(item model.ServiceRecord) bool { return item.Cost >= low && item.Cost <= high })
}

// TotalCost adds up the cost of every record.
func (s *ServiceRecordStore) TotalCost() float64 {
	var total float64
	for _, item := range s.List() {
		total += item.Cost
	}
	return total
}

// AverageCost is the mean cost (0 when there are no records).
func (s *ServiceRecordStore) AverageCost() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalCost()) / float64(len(items))
}

// MaxCost returns the record with the highest cost.
func (s *ServiceRecordStore) MaxCost() (model.ServiceRecord, bool) {
	var best model.ServiceRecord
	found := false
	for _, item := range s.List() {
		if !found || item.Cost > best.Cost {
			best, found = item, true
		}
	}
	return best, found
}

// WithKind returns records whose kind is value.
func (s *ServiceRecordStore) WithKind(value model.ServiceRecordKind) []model.ServiceRecord {
	return s.Filter(func(item model.ServiceRecord) bool { return item.Kind == value })
}

// CountByKind counts records for every kind.
func (s *ServiceRecordStore) CountByKind() map[model.ServiceRecordKind]int {
	counts := map[model.ServiceRecordKind]int{}
	for _, v := range model.ServiceRecordKindValues {
		counts[v] = 0
	}
	for _, item := range s.List() {
		counts[item.Kind]++
	}
	return counts
}

// FindByNotes returns records whose notes is exactly value.
func (s *ServiceRecordStore) FindByNotes(value string) []model.ServiceRecord {
	return s.Filter(func(item model.ServiceRecord) bool { return item.Notes == value })
}

// SearchNotes returns records whose notes contains text (any case).
func (s *ServiceRecordStore) SearchNotes(text string) []model.ServiceRecord {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.ServiceRecord) bool { return strings.Contains(strings.ToLower(item.Notes), needle) })
}

// Search returns records where any text field contains text (any case).
func (s *ServiceRecordStore) Search(text string) []model.ServiceRecord {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.ServiceRecord) bool {
		for _, value := range []string{item.Notes} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// IncidentStore keeps every incident.
type IncidentStore struct {
	mu     sync.RWMutex
	items  map[int]model.Incident
	nextID int
}

// NewIncidentStore returns an empty store.
func NewIncidentStore() *IncidentStore {
	return &IncidentStore{items: map[int]model.Incident{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *IncidentStore) Create(item model.Incident) model.Incident {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *IncidentStore) Get(id int) (model.Incident, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *IncidentStore) List() []model.Incident {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.Incident, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *IncidentStore) Update(item model.Incident) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *IncidentStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *IncidentStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *IncidentStore) Filter(keep func(model.Incident) bool) []model.Incident {
	out := []model.Incident{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// ForVehicle returns records linked to vehicle id.
func (s *IncidentStore) ForVehicle(id int) []model.Incident {
	return s.Filter(func(item model.Incident) bool { return item.VehicleID == id })
}

// CountForVehicle counts records linked to vehicle id.
func (s *IncidentStore) CountForVehicle(id int) int {
	return len(s.ForVehicle(id))
}

// ForDriver returns records linked to driver id.
func (s *IncidentStore) ForDriver(id int) []model.Incident {
	return s.Filter(func(item model.Incident) bool { return item.DriverID == id })
}

// CountForDriver counts records linked to driver id.
func (s *IncidentStore) CountForDriver(id int) int {
	return len(s.ForDriver(id))
}

// HappenedBefore returns records whose happened is before day (YYYY-MM-DD).
func (s *IncidentStore) HappenedBefore(day string) []model.Incident {
	return s.Filter(func(item model.Incident) bool { return item.Happened < day })
}

// HappenedAfter returns records whose happened is after day (YYYY-MM-DD).
func (s *IncidentStore) HappenedAfter(day string) []model.Incident {
	return s.Filter(func(item model.Incident) bool { return item.Happened > day })
}

// HappenedOn returns records whose happened is day.
func (s *IncidentStore) HappenedOn(day string) []model.Incident {
	return s.Filter(func(item model.Incident) bool { return item.Happened == day })
}

// WithSeverity returns records whose severity is value.
func (s *IncidentStore) WithSeverity(value model.IncidentSeverity) []model.Incident {
	return s.Filter(func(item model.Incident) bool { return item.Severity == value })
}

// CountBySeverity counts records for every severity.
func (s *IncidentStore) CountBySeverity() map[model.IncidentSeverity]int {
	counts := map[model.IncidentSeverity]int{}
	for _, v := range model.IncidentSeverityValues {
		counts[v] = 0
	}
	for _, item := range s.List() {
		counts[item.Severity]++
	}
	return counts
}

// BetweenDamageCost returns records whose damage cost is within [low, high].
func (s *IncidentStore) BetweenDamageCost(low, high float64) []model.Incident {
	return s.Filter(func(item model.Incident) bool { return item.DamageCost >= low && item.DamageCost <= high })
}

// TotalDamageCost adds up the damage cost of every record.
func (s *IncidentStore) TotalDamageCost() float64 {
	var total float64
	for _, item := range s.List() {
		total += item.DamageCost
	}
	return total
}

// AverageDamageCost is the mean damage cost (0 when there are no records).
func (s *IncidentStore) AverageDamageCost() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalDamageCost()) / float64(len(items))
}

// MaxDamageCost returns the record with the highest damage cost.
func (s *IncidentStore) MaxDamageCost() (model.Incident, bool) {
	var best model.Incident
	found := false
	for _, item := range s.List() {
		if !found || item.DamageCost > best.DamageCost {
			best, found = item, true
		}
	}
	return best, found
}

// WhereReported returns records whose reported flag equals flag.
func (s *IncidentStore) WhereReported(flag bool) []model.Incident {
	return s.Filter(func(item model.Incident) bool { return item.Reported == flag })
}

// Search returns records where any text field contains text (any case).
func (s *IncidentStore) Search(text string) []model.Incident {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Incident) bool {
		return needle == ""
	})
}

// DocumentStore keeps every document.
type DocumentStore struct {
	mu     sync.RWMutex
	items  map[int]model.Document
	nextID int
}

// NewDocumentStore returns an empty store.
func NewDocumentStore() *DocumentStore {
	return &DocumentStore{items: map[int]model.Document{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *DocumentStore) Create(item model.Document) model.Document {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *DocumentStore) Get(id int) (model.Document, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *DocumentStore) List() []model.Document {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.Document, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *DocumentStore) Update(item model.Document) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *DocumentStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *DocumentStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *DocumentStore) Filter(keep func(model.Document) bool) []model.Document {
	out := []model.Document{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// ForVehicle returns records linked to vehicle id.
func (s *DocumentStore) ForVehicle(id int) []model.Document {
	return s.Filter(func(item model.Document) bool { return item.VehicleID == id })
}

// CountForVehicle counts records linked to vehicle id.
func (s *DocumentStore) CountForVehicle(id int) int {
	return len(s.ForVehicle(id))
}

// FindByTitle returns records whose title is exactly value.
func (s *DocumentStore) FindByTitle(value string) []model.Document {
	return s.Filter(func(item model.Document) bool { return item.Title == value })
}

// SearchTitle returns records whose title contains text (any case).
func (s *DocumentStore) SearchTitle(text string) []model.Document {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Document) bool { return strings.Contains(strings.ToLower(item.Title), needle) })
}

// BetweenPages returns records whose pages is within [low, high].
func (s *DocumentStore) BetweenPages(low, high int) []model.Document {
	return s.Filter(func(item model.Document) bool { return item.Pages >= low && item.Pages <= high })
}

// TotalPages adds up the pages of every record.
func (s *DocumentStore) TotalPages() int {
	var total int
	for _, item := range s.List() {
		total += item.Pages
	}
	return total
}

// AveragePages is the mean pages (0 when there are no records).
func (s *DocumentStore) AveragePages() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalPages()) / float64(len(items))
}

// MaxPages returns the record with the highest pages.
func (s *DocumentStore) MaxPages() (model.Document, bool) {
	var best model.Document
	found := false
	for _, item := range s.List() {
		if !found || item.Pages > best.Pages {
			best, found = item, true
		}
	}
	return best, found
}

// WhereSigned returns records whose signed flag equals flag.
func (s *DocumentStore) WhereSigned(flag bool) []model.Document {
	return s.Filter(func(item model.Document) bool { return item.Signed == flag })
}

// BetweenVersion returns records whose version is within [low, high].
func (s *DocumentStore) BetweenVersion(low, high int) []model.Document {
	return s.Filter(func(item model.Document) bool { return item.Version >= low && item.Version <= high })
}

// TotalVersion adds up the version of every record.
func (s *DocumentStore) TotalVersion() int {
	var total int
	for _, item := range s.List() {
		total += item.Version
	}
	return total
}

// AverageVersion is the mean version (0 when there are no records).
func (s *DocumentStore) AverageVersion() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalVersion()) / float64(len(items))
}

// MaxVersion returns the record with the highest version.
func (s *DocumentStore) MaxVersion() (model.Document, bool) {
	var best model.Document
	found := false
	for _, item := range s.List() {
		if !found || item.Version > best.Version {
			best, found = item, true
		}
	}
	return best, found
}

// IssuedBefore returns records whose issued is before day (YYYY-MM-DD).
func (s *DocumentStore) IssuedBefore(day string) []model.Document {
	return s.Filter(func(item model.Document) bool { return item.Issued < day })
}

// IssuedAfter returns records whose issued is after day (YYYY-MM-DD).
func (s *DocumentStore) IssuedAfter(day string) []model.Document {
	return s.Filter(func(item model.Document) bool { return item.Issued > day })
}

// IssuedOn returns records whose issued is day.
func (s *DocumentStore) IssuedOn(day string) []model.Document {
	return s.Filter(func(item model.Document) bool { return item.Issued == day })
}

// Search returns records where any text field contains text (any case).
func (s *DocumentStore) Search(text string) []model.Document {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Document) bool {
		for _, value := range []string{item.Title} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// NotificationStore keeps every notification.
type NotificationStore struct {
	mu     sync.RWMutex
	items  map[int]model.Notification
	nextID int
}

// NewNotificationStore returns an empty store.
func NewNotificationStore() *NotificationStore {
	return &NotificationStore{items: map[int]model.Notification{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *NotificationStore) Create(item model.Notification) model.Notification {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *NotificationStore) Get(id int) (model.Notification, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *NotificationStore) List() []model.Notification {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.Notification, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *NotificationStore) Update(item model.Notification) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *NotificationStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *NotificationStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *NotificationStore) Filter(keep func(model.Notification) bool) []model.Notification {
	out := []model.Notification{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// FindByRecipient returns records whose recipient is exactly value.
func (s *NotificationStore) FindByRecipient(value string) []model.Notification {
	return s.Filter(func(item model.Notification) bool { return item.Recipient == value })
}

// SearchRecipient returns records whose recipient contains text (any case).
func (s *NotificationStore) SearchRecipient(text string) []model.Notification {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Notification) bool { return strings.Contains(strings.ToLower(item.Recipient), needle) })
}

// FindByTitle returns records whose title is exactly value.
func (s *NotificationStore) FindByTitle(value string) []model.Notification {
	return s.Filter(func(item model.Notification) bool { return item.Title == value })
}

// SearchTitle returns records whose title contains text (any case).
func (s *NotificationStore) SearchTitle(text string) []model.Notification {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Notification) bool { return strings.Contains(strings.ToLower(item.Title), needle) })
}

// SentBefore returns records whose sent is before day (YYYY-MM-DD).
func (s *NotificationStore) SentBefore(day string) []model.Notification {
	return s.Filter(func(item model.Notification) bool { return item.Sent < day })
}

// SentAfter returns records whose sent is after day (YYYY-MM-DD).
func (s *NotificationStore) SentAfter(day string) []model.Notification {
	return s.Filter(func(item model.Notification) bool { return item.Sent > day })
}

// SentOn returns records whose sent is day.
func (s *NotificationStore) SentOn(day string) []model.Notification {
	return s.Filter(func(item model.Notification) bool { return item.Sent == day })
}

// WithChannel returns records whose channel is value.
func (s *NotificationStore) WithChannel(value model.NotificationChannel) []model.Notification {
	return s.Filter(func(item model.Notification) bool { return item.Channel == value })
}

// CountByChannel counts records for every channel.
func (s *NotificationStore) CountByChannel() map[model.NotificationChannel]int {
	counts := map[model.NotificationChannel]int{}
	for _, v := range model.NotificationChannelValues {
		counts[v] = 0
	}
	for _, item := range s.List() {
		counts[item.Channel]++
	}
	return counts
}

// WhereRead returns records whose read flag equals flag.
func (s *NotificationStore) WhereRead(flag bool) []model.Notification {
	return s.Filter(func(item model.Notification) bool { return item.Read == flag })
}

// Search returns records where any text field contains text (any case).
func (s *NotificationStore) Search(text string) []model.Notification {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Notification) bool {
		for _, value := range []string{item.Recipient, item.Title} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}
