package service_test

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"fleet-api/internal/httpapi"
	"fleet-api/internal/model"
	"fleet-api/internal/service"
)

func seeded(t *testing.T) *service.Service {
	t.Helper()
	svc := service.New()
	if err := svc.Seed(3); err != nil {
		t.Fatalf("seed: %v", err)
	}
	return svc
}

func wantField(t *testing.T, err error, field string) {
	t.Helper()
	var invalid *model.ValidationError
	if !errors.As(err, &invalid) || invalid.Field != field {
		t.Fatalf("want a validation error on %q, got %v", field, err)
	}
}

func call(t *testing.T, h http.Handler, method, path string, body any) *httptest.ResponseRecorder {
	t.Helper()
	var reader *bytes.Reader
	if body == nil {
		reader = bytes.NewReader(nil)
	} else {
		data, err := json.Marshal(body)
		if err != nil {
			t.Fatalf("marshal: %v", err)
		}
		reader = bytes.NewReader(data)
	}
	rec := httptest.NewRecorder()
	h.ServeHTTP(rec, httptest.NewRequest(method, path, reader))
	return rec
}

// keep the imports used even for domains without text fields
var _ = strings.ToUpper

func TestVehicleCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateVehicle(service.SampleVehicle(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetVehicle(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListVehicles()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestVehicleMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetVehicle(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestVehicleRejectsBadPlate(t *testing.T) {
	svc := seeded(t)
	item := service.SampleVehicle(12)
	item.Plate = ""
	_, err := svc.CreateVehicle(item)
	wantField(t, err, "plate")
}

func TestVehicleRejectsBadMake(t *testing.T) {
	svc := seeded(t)
	item := service.SampleVehicle(12)
	item.Make = ""
	_, err := svc.CreateVehicle(item)
	wantField(t, err, "make")
}

func TestVehicleRejectsBadModel(t *testing.T) {
	svc := seeded(t)
	item := service.SampleVehicle(12)
	item.Model = ""
	_, err := svc.CreateVehicle(item)
	wantField(t, err, "model")
}

func TestVehicleRejectsBadYear(t *testing.T) {
	svc := seeded(t)
	item := service.SampleVehicle(12)
	item.Year = -1
	_, err := svc.CreateVehicle(item)
	wantField(t, err, "year")
}

func TestVehicleRejectsBadMileage(t *testing.T) {
	svc := seeded(t)
	item := service.SampleVehicle(12)
	item.Mileage = -1
	_, err := svc.CreateVehicle(item)
	wantField(t, err, "mileage")
}

func TestVehicleRejectsBadFuel(t *testing.T) {
	svc := seeded(t)
	item := service.SampleVehicle(12)
	item.Fuel = "nope"
	_, err := svc.CreateVehicle(item)
	wantField(t, err, "fuel")
}

func TestSearchVehiclePlate(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetVehicle(2)
	for _, item := range svc.Vehicles.SearchPlate(strings.ToUpper(target.Plate)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Plate)
}

func TestSearchVehicleMake(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetVehicle(2)
	for _, item := range svc.Vehicles.SearchMake(strings.ToUpper(target.Make)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Make)
}

func TestSearchVehicleModel(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetVehicle(2)
	for _, item := range svc.Vehicles.SearchModel(strings.ToUpper(target.Model)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Model)
}

func TestAdjustVehicleYear(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetVehicle(1)
	after, err := svc.AdjustVehicleYear(1, 2)
	if err != nil || after.Year != before.Year+2 {
		t.Fatalf("adjust = %v, %v", after.Year, err)
	}
	_, err = svc.AdjustVehicleYear(1, -(after.Year + 100))
	wantField(t, err, "year")
}

func TestAdjustVehicleMileage(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetVehicle(1)
	after, err := svc.AdjustVehicleMileage(1, 2)
	if err != nil || after.Mileage != before.Mileage+2 {
		t.Fatalf("adjust = %v, %v", after.Mileage, err)
	}
	_, err = svc.AdjustVehicleMileage(1, -(after.Mileage + 100))
	wantField(t, err, "mileage")
}

func TestSetVehicleFuel(t *testing.T) {
	svc := seeded(t)
	last := model.VehicleFuelValues[len(model.VehicleFuelValues)-1]
	item, err := svc.SetVehicleFuel(1, last)
	if err != nil || item.Fuel != last {
		t.Fatalf("set = %v, %v", item.Fuel, err)
	}
	if got, want := svc.Vehicles.CountByFuel()[last], len(svc.Vehicles.WithFuel(last)); got != want {
		t.Fatalf("count %d != %d", got, want)
	}
}

func TestToggleVehicleActive(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetVehicle(1)
	after, err := svc.ToggleVehicleActive(1)
	if err != nil || after.Active == before.Active {
		t.Fatalf("toggle = %v, %v", after.Active, err)
	}
}

func TestDeleteVehicle(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateVehicle(service.SampleVehicle(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteVehicle(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetVehicle(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestDeleteVehicleInUse(t *testing.T) {
	svc := seeded(t)
	if err := svc.DeleteVehicle(1); !errors.Is(err, service.ErrConflict) {
		t.Fatalf("want ErrConflict, got %v", err)
	}
}

func TestVehicleStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.VehicleStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}

func TestVehicleAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/vehicles", service.SampleVehicle(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.Vehicle
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/vehicles/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/vehicles?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/vehicles/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/vehicles", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}

func TestDriverCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateDriver(service.SampleDriver(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetDriver(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListDrivers()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestDriverMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetDriver(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestDriverRejectsBadName(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDriver(12)
	item.Name = ""
	_, err := svc.CreateDriver(item)
	wantField(t, err, "name")
}

func TestDriverRejectsBadEmail(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDriver(12)
	item.Email = "not-an-email"
	_, err := svc.CreateDriver(item)
	wantField(t, err, "email")
}

func TestDriverRejectsBadLicenseNo(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDriver(12)
	item.LicenseNo = ""
	_, err := svc.CreateDriver(item)
	wantField(t, err, "license_no")
}

func TestDriverRejectsBadLicenseExpiry(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDriver(12)
	item.LicenseExpiry = "2026-02-30"
	_, err := svc.CreateDriver(item)
	wantField(t, err, "license_expiry")
}

func TestDriverRejectsBadRating(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDriver(12)
	item.Rating = -1
	_, err := svc.CreateDriver(item)
	wantField(t, err, "rating")
}

func TestSearchDriverName(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetDriver(2)
	for _, item := range svc.Drivers.SearchName(strings.ToUpper(target.Name)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Name)
}

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

func TestDriverAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/drivers", service.SampleDriver(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.Driver
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/drivers/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/drivers?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/drivers/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/drivers", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}

func TestTripCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateTrip(service.SampleTrip(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetTrip(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListTrips()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestTripMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetTrip(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestTripRejectsBadVehicleID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleTrip(12)
	item.VehicleID = 0
	_, err := svc.CreateTrip(item)
	wantField(t, err, "vehicle_id")
}

func TestTripRejectsBadDriverID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleTrip(12)
	item.DriverID = 0
	_, err := svc.CreateTrip(item)
	wantField(t, err, "driver_id")
}

func TestTripRejectsBadStarted(t *testing.T) {
	svc := seeded(t)
	item := service.SampleTrip(12)
	item.Started = "2026-02-30"
	_, err := svc.CreateTrip(item)
	wantField(t, err, "started")
}

func TestTripRejectsBadDistanceKm(t *testing.T) {
	svc := seeded(t)
	item := service.SampleTrip(12)
	item.DistanceKm = -1
	_, err := svc.CreateTrip(item)
	wantField(t, err, "distance_km")
}

func TestTripRejectsBadPurpose(t *testing.T) {
	svc := seeded(t)
	item := service.SampleTrip(12)
	item.Purpose = ""
	_, err := svc.CreateTrip(item)
	wantField(t, err, "purpose")
}

func TestTripRejectsBadStatus(t *testing.T) {
	svc := seeded(t)
	item := service.SampleTrip(12)
	item.Status = "nope"
	_, err := svc.CreateTrip(item)
	wantField(t, err, "status")
}

func TestTripVehicleIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleTrip(13)
	item.VehicleID = 9999
	if _, err := svc.CreateTrip(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestTripDriverIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleTrip(13)
	item.DriverID = 9999
	if _, err := svc.CreateTrip(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestTripStartedRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SampleTrip(2).Started
	total := len(svc.Trips.StartedBefore(day)) + len(svc.Trips.StartedOn(day)) + len(svc.Trips.StartedAfter(day))
	if total != svc.Trips.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.Trips.Count())
	}
}

func TestAdjustTripDistanceKm(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetTrip(1)
	after, err := svc.AdjustTripDistanceKm(1, 1.5)
	if err != nil || after.DistanceKm-before.DistanceKm < 1.49 || after.DistanceKm-before.DistanceKm > 1.51 {
		t.Fatalf("adjust = %v, %v", after.DistanceKm, err)
	}
}

func TestSearchTripPurpose(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetTrip(2)
	for _, item := range svc.Trips.SearchPurpose(strings.ToUpper(target.Purpose)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Purpose)
}

func TestSetTripStatus(t *testing.T) {
	svc := seeded(t)
	last := model.TripStatusValues[len(model.TripStatusValues)-1]
	item, err := svc.SetTripStatus(1, last)
	if err != nil || item.Status != last {
		t.Fatalf("set = %v, %v", item.Status, err)
	}
	if got, want := svc.Trips.CountByStatus()[last], len(svc.Trips.WithStatus(last)); got != want {
		t.Fatalf("count %d != %d", got, want)
	}
}

func TestDeleteTrip(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateTrip(service.SampleTrip(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteTrip(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetTrip(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestTripStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.TripStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}

func TestTripAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/trips", service.SampleTrip(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.Trip
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/trips/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/trips?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/trips/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/trips", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}

func TestFuelLogCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateFuelLog(service.SampleFuelLog(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetFuelLog(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListFuelLogs()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestFuelLogMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetFuelLog(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestFuelLogRejectsBadVehicleID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleFuelLog(12)
	item.VehicleID = 0
	_, err := svc.CreateFuelLog(item)
	wantField(t, err, "vehicle_id")
}

func TestFuelLogRejectsBadFilled(t *testing.T) {
	svc := seeded(t)
	item := service.SampleFuelLog(12)
	item.Filled = "2026-02-30"
	_, err := svc.CreateFuelLog(item)
	wantField(t, err, "filled")
}

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

func TestDeleteFuelLog(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateFuelLog(service.SampleFuelLog(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteFuelLog(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetFuelLog(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestFuelLogStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.FuelLogStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}

func TestFuelLogAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/fuel-logs", service.SampleFuelLog(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.FuelLog
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/fuel-logs/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/fuel-logs?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/fuel-logs/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/fuel-logs", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}

func TestServiceRecordCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateServiceRecord(service.SampleServiceRecord(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetServiceRecord(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListServiceRecords()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestServiceRecordMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetServiceRecord(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestServiceRecordRejectsBadVehicleID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleServiceRecord(12)
	item.VehicleID = 0
	_, err := svc.CreateServiceRecord(item)
	wantField(t, err, "vehicle_id")
}

func TestServiceRecordRejectsBadServiced(t *testing.T) {
	svc := seeded(t)
	item := service.SampleServiceRecord(12)
	item.Serviced = "2026-02-30"
	_, err := svc.CreateServiceRecord(item)
	wantField(t, err, "serviced")
}

func TestServiceRecordRejectsBadOdometer(t *testing.T) {
	svc := seeded(t)
	item := service.SampleServiceRecord(12)
	item.Odometer = -1
	_, err := svc.CreateServiceRecord(item)
	wantField(t, err, "odometer")
}

func TestServiceRecordRejectsBadCost(t *testing.T) {
	svc := seeded(t)
	item := service.SampleServiceRecord(12)
	item.Cost = -5
	_, err := svc.CreateServiceRecord(item)
	wantField(t, err, "cost")
}

func TestServiceRecordRejectsBadKind(t *testing.T) {
	svc := seeded(t)
	item := service.SampleServiceRecord(12)
	item.Kind = "nope"
	_, err := svc.CreateServiceRecord(item)
	wantField(t, err, "kind")
}

func TestServiceRecordRejectsBadNotes(t *testing.T) {
	svc := seeded(t)
	item := service.SampleServiceRecord(12)
	item.Notes = strings.Repeat("x", 3000)
	_, err := svc.CreateServiceRecord(item)
	wantField(t, err, "notes")
}

func TestServiceRecordVehicleIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleServiceRecord(13)
	item.VehicleID = 9999
	if _, err := svc.CreateServiceRecord(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

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

func TestServiceRecordStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.ServiceRecordStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}

func TestServiceRecordAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/service-records", service.SampleServiceRecord(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.ServiceRecord
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/service-records/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/service-records?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/service-records/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/service-records", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}

func TestIncidentCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateIncident(service.SampleIncident(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetIncident(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListIncidents()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestIncidentMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetIncident(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestIncidentRejectsBadVehicleID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleIncident(12)
	item.VehicleID = 0
	_, err := svc.CreateIncident(item)
	wantField(t, err, "vehicle_id")
}

func TestIncidentRejectsBadDriverID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleIncident(12)
	item.DriverID = 0
	_, err := svc.CreateIncident(item)
	wantField(t, err, "driver_id")
}

func TestIncidentRejectsBadHappened(t *testing.T) {
	svc := seeded(t)
	item := service.SampleIncident(12)
	item.Happened = "2026-02-30"
	_, err := svc.CreateIncident(item)
	wantField(t, err, "happened")
}

func TestIncidentRejectsBadSeverity(t *testing.T) {
	svc := seeded(t)
	item := service.SampleIncident(12)
	item.Severity = "nope"
	_, err := svc.CreateIncident(item)
	wantField(t, err, "severity")
}

func TestIncidentRejectsBadDamageCost(t *testing.T) {
	svc := seeded(t)
	item := service.SampleIncident(12)
	item.DamageCost = -5
	_, err := svc.CreateIncident(item)
	wantField(t, err, "damage_cost")
}

func TestIncidentVehicleIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleIncident(13)
	item.VehicleID = 9999
	if _, err := svc.CreateIncident(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestIncidentDriverIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleIncident(13)
	item.DriverID = 9999
	if _, err := svc.CreateIncident(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

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

func TestIncidentAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/incidents", service.SampleIncident(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.Incident
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/incidents/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/incidents?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/incidents/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/incidents", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}

func TestDocumentCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateDocument(service.SampleDocument(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetDocument(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListDocuments()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestDocumentMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetDocument(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestDocumentRejectsBadVehicleID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDocument(12)
	item.VehicleID = 0
	_, err := svc.CreateDocument(item)
	wantField(t, err, "vehicle_id")
}

func TestDocumentRejectsBadTitle(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDocument(12)
	item.Title = ""
	_, err := svc.CreateDocument(item)
	wantField(t, err, "title")
}

func TestDocumentRejectsBadPages(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDocument(12)
	item.Pages = -1
	_, err := svc.CreateDocument(item)
	wantField(t, err, "pages")
}

func TestDocumentRejectsBadVersion(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDocument(12)
	item.Version = -1
	_, err := svc.CreateDocument(item)
	wantField(t, err, "version")
}

func TestDocumentRejectsBadIssued(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDocument(12)
	item.Issued = "2026-02-30"
	_, err := svc.CreateDocument(item)
	wantField(t, err, "issued")
}

func TestDocumentVehicleIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDocument(13)
	item.VehicleID = 9999
	if _, err := svc.CreateDocument(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestSearchDocumentTitle(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetDocument(2)
	for _, item := range svc.Documents.SearchTitle(strings.ToUpper(target.Title)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Title)
}

func TestAdjustDocumentPages(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetDocument(1)
	after, err := svc.AdjustDocumentPages(1, 2)
	if err != nil || after.Pages != before.Pages+2 {
		t.Fatalf("adjust = %v, %v", after.Pages, err)
	}
	_, err = svc.AdjustDocumentPages(1, -(after.Pages + 100))
	wantField(t, err, "pages")
}

func TestToggleDocumentSigned(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetDocument(1)
	after, err := svc.ToggleDocumentSigned(1)
	if err != nil || after.Signed == before.Signed {
		t.Fatalf("toggle = %v, %v", after.Signed, err)
	}
}

func TestAdjustDocumentVersion(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetDocument(1)
	after, err := svc.AdjustDocumentVersion(1, 2)
	if err != nil || after.Version != before.Version+2 {
		t.Fatalf("adjust = %v, %v", after.Version, err)
	}
	_, err = svc.AdjustDocumentVersion(1, -(after.Version + 100))
	wantField(t, err, "version")
}

func TestDocumentIssuedRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SampleDocument(2).Issued
	total := len(svc.Documents.IssuedBefore(day)) + len(svc.Documents.IssuedOn(day)) + len(svc.Documents.IssuedAfter(day))
	if total != svc.Documents.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.Documents.Count())
	}
}

func TestDeleteDocument(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateDocument(service.SampleDocument(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteDocument(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetDocument(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestDocumentStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.DocumentStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}

func TestDocumentAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/documents", service.SampleDocument(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.Document
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/documents/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/documents?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/documents/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/documents", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}

func TestNotificationCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateNotification(service.SampleNotification(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetNotification(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListNotifications()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestNotificationMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetNotification(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestNotificationRejectsBadRecipient(t *testing.T) {
	svc := seeded(t)
	item := service.SampleNotification(12)
	item.Recipient = "not-an-email"
	_, err := svc.CreateNotification(item)
	wantField(t, err, "recipient")
}

func TestNotificationRejectsBadTitle(t *testing.T) {
	svc := seeded(t)
	item := service.SampleNotification(12)
	item.Title = ""
	_, err := svc.CreateNotification(item)
	wantField(t, err, "title")
}

func TestNotificationRejectsBadSent(t *testing.T) {
	svc := seeded(t)
	item := service.SampleNotification(12)
	item.Sent = "2026-02-30"
	_, err := svc.CreateNotification(item)
	wantField(t, err, "sent")
}

func TestNotificationRejectsBadChannel(t *testing.T) {
	svc := seeded(t)
	item := service.SampleNotification(12)
	item.Channel = "nope"
	_, err := svc.CreateNotification(item)
	wantField(t, err, "channel")
}

func TestSearchNotificationRecipient(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetNotification(2)
	for _, item := range svc.Notifications.SearchRecipient(strings.ToUpper(target.Recipient)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Recipient)
}

func TestSearchNotificationTitle(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetNotification(2)
	for _, item := range svc.Notifications.SearchTitle(strings.ToUpper(target.Title)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Title)
}

func TestNotificationSentRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SampleNotification(2).Sent
	total := len(svc.Notifications.SentBefore(day)) + len(svc.Notifications.SentOn(day)) + len(svc.Notifications.SentAfter(day))
	if total != svc.Notifications.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.Notifications.Count())
	}
}

func TestSetNotificationChannel(t *testing.T) {
	svc := seeded(t)
	last := model.NotificationChannelValues[len(model.NotificationChannelValues)-1]
	item, err := svc.SetNotificationChannel(1, last)
	if err != nil || item.Channel != last {
		t.Fatalf("set = %v, %v", item.Channel, err)
	}
	if got, want := svc.Notifications.CountByChannel()[last], len(svc.Notifications.WithChannel(last)); got != want {
		t.Fatalf("count %d != %d", got, want)
	}
}

func TestToggleNotificationRead(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetNotification(1)
	after, err := svc.ToggleNotificationRead(1)
	if err != nil || after.Read == before.Read {
		t.Fatalf("toggle = %v, %v", after.Read, err)
	}
}

func TestDeleteNotification(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateNotification(service.SampleNotification(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteNotification(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetNotification(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestNotificationStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.NotificationStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}

func TestNotificationAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/notifications", service.SampleNotification(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.Notification
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/notifications/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/notifications?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/notifications/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/notifications", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}
