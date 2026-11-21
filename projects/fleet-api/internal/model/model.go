// Package model holds the Fleet Management records and their validation rules.
package model

import (
	"cmp"
	"errors"
	"fmt"
	"math"
	"regexp"
	"strings"
	"time"
)

var emailPattern = regexp.MustCompile(`^[^@\s]+@[^@\s]+\.[^@\s]+$`)

// ValidationError reports a field holding a value the service can't accept.
type ValidationError struct {
	Field   string
	Message string
}

func (e *ValidationError) Error() string { return e.Field + ": " + e.Message }

// Invalid builds a ValidationError.
func Invalid(field, format string, args ...any) error {
	return &ValidationError{Field: field, Message: fmt.Sprintf(format, args...)}
}

// IsValidation reports whether err is (or wraps) a ValidationError.
func IsValidation(err error) bool {
	var v *ValidationError
	return errors.As(err, &v)
}

// CheckText trims value and checks it isn't empty (unless optional) or too long.
func CheckText(field, value string, max int, required bool) (string, error) {
	cleaned := strings.TrimSpace(value)
	if required && cleaned == "" {
		return "", Invalid(field, "is required")
	}
	if len(cleaned) > max {
		return "", Invalid(field, "must be at most %d characters", max)
	}
	return cleaned, nil
}

// CheckEmail checks for a plausible e-mail address and lower-cases it.
func CheckEmail(field, value string) (string, error) {
	text, err := CheckText(field, value, 254, true)
	if err != nil {
		return "", err
	}
	if !emailPattern.MatchString(text) {
		return "", Invalid(field, "must be an e-mail address")
	}
	return strings.ToLower(text), nil
}

// CheckInt rejects negative numbers.
func CheckInt(field string, value int) error {
	if value < 0 {
		return Invalid(field, "must be at least 0")
	}
	if value > 1_000_000_000 {
		return Invalid(field, "must be at most 1000000000")
	}
	return nil
}

// CheckNumber rejects negative amounts.
func CheckNumber(field string, value float64) error {
	if value < 0 {
		return Invalid(field, "must be at least 0")
	}
	return nil
}

// CheckDate wants an ISO date (YYYY-MM-DD) that exists in the calendar.
func CheckDate(field, value string) error {
	if _, err := time.Parse("2006-01-02", value); err != nil {
		return Invalid(field, "must be a real date like 2026-01-31")
	}
	return nil
}

// CheckRef wants the id of another record (existence is checked by the service).
func CheckRef(field string, value int) error {
	if value < 1 {
		return Invalid(field, "must point at a record")
	}
	return nil
}

// VehicleFuel is the fuel of a Vehicle.
type VehicleFuel string

// Allowed VehicleFuel values.
const (
	VehicleFuelPetrol   VehicleFuel = "petrol"
	VehicleFuelDiesel   VehicleFuel = "diesel"
	VehicleFuelElectric VehicleFuel = "electric"
	VehicleFuelHybrid   VehicleFuel = "hybrid"
)

// VehicleFuelValues lists every allowed VehicleFuel.
var VehicleFuelValues = []VehicleFuel{VehicleFuelPetrol, VehicleFuelDiesel, VehicleFuelElectric, VehicleFuelHybrid}

// Valid reports whether v is one of the allowed values.
func (v VehicleFuel) Valid() bool {
	for _, allowed := range VehicleFuelValues {
		if v == allowed {
			return true
		}
	}
	return false
}

// Label is a human-friendly name for v.
func (v VehicleFuel) Label() string {
	text := strings.ReplaceAll(string(v), "_", " ")
	return strings.ToUpper(text[:1]) + text[1:]
}

// ParseVehicleFuel turns text into a VehicleFuel.
func ParseVehicleFuel(text string) (VehicleFuel, error) {
	v := VehicleFuel(strings.ToLower(strings.TrimSpace(text)))
	if !v.Valid() {
		return "", Invalid("fuel", "must be one of %s", VehicleFuelList())
	}
	return v, nil
}

// VehicleFuelList is every allowed value, comma separated.
func VehicleFuelList() string {
	parts := make([]string, len(VehicleFuelValues))
	for i, v := range VehicleFuelValues {
		parts[i] = string(v)
	}
	return strings.Join(parts, ", ")
}

// TripStatus is the status of a Trip.
type TripStatus string

// Allowed TripStatus values.
const (
	TripStatusPlanned    TripStatus = "planned"
	TripStatusInProgress TripStatus = "in_progress"
	TripStatusDone       TripStatus = "done"
	TripStatusCancelled  TripStatus = "cancelled"
)

// TripStatusValues lists every allowed TripStatus.
var TripStatusValues = []TripStatus{TripStatusPlanned, TripStatusInProgress, TripStatusDone, TripStatusCancelled}

// Valid reports whether v is one of the allowed values.
func (v TripStatus) Valid() bool {
	for _, allowed := range TripStatusValues {
		if v == allowed {
			return true
		}
	}
	return false
}

// Label is a human-friendly name for v.
func (v TripStatus) Label() string {
	text := strings.ReplaceAll(string(v), "_", " ")
	return strings.ToUpper(text[:1]) + text[1:]
}

// ParseTripStatus turns text into a TripStatus.
func ParseTripStatus(text string) (TripStatus, error) {
	v := TripStatus(strings.ToLower(strings.TrimSpace(text)))
	if !v.Valid() {
		return "", Invalid("status", "must be one of %s", TripStatusList())
	}
	return v, nil
}

// TripStatusList is every allowed value, comma separated.
func TripStatusList() string {
	parts := make([]string, len(TripStatusValues))
	for i, v := range TripStatusValues {
		parts[i] = string(v)
	}
	return strings.Join(parts, ", ")
}

// ServiceRecordKind is the kind of a ServiceRecord.
type ServiceRecordKind string

// Allowed ServiceRecordKind values.
const (
	ServiceRecordKindOil        ServiceRecordKind = "oil"
	ServiceRecordKindTyres      ServiceRecordKind = "tyres"
	ServiceRecordKindBrakes     ServiceRecordKind = "brakes"
	ServiceRecordKindInspection ServiceRecordKind = "inspection"
	ServiceRecordKindRepair     ServiceRecordKind = "repair"
)

// ServiceRecordKindValues lists every allowed ServiceRecordKind.
var ServiceRecordKindValues = []ServiceRecordKind{ServiceRecordKindOil, ServiceRecordKindTyres, ServiceRecordKindBrakes, ServiceRecordKindInspection, ServiceRecordKindRepair}

// Valid reports whether v is one of the allowed values.
func (v ServiceRecordKind) Valid() bool {
	for _, allowed := range ServiceRecordKindValues {
		if v == allowed {
			return true
		}
	}
	return false
}

// Label is a human-friendly name for v.
func (v ServiceRecordKind) Label() string {
	text := strings.ReplaceAll(string(v), "_", " ")
	return strings.ToUpper(text[:1]) + text[1:]
}

// ParseServiceRecordKind turns text into a ServiceRecordKind.
func ParseServiceRecordKind(text string) (ServiceRecordKind, error) {
	v := ServiceRecordKind(strings.ToLower(strings.TrimSpace(text)))
	if !v.Valid() {
		return "", Invalid("kind", "must be one of %s", ServiceRecordKindList())
	}
	return v, nil
}

// ServiceRecordKindList is every allowed value, comma separated.
func ServiceRecordKindList() string {
	parts := make([]string, len(ServiceRecordKindValues))
	for i, v := range ServiceRecordKindValues {
		parts[i] = string(v)
	}
	return strings.Join(parts, ", ")
}

// IncidentSeverity is the severity of a Incident.
type IncidentSeverity string

// Allowed IncidentSeverity values.
const (
	IncidentSeverityMinor    IncidentSeverity = "minor"
	IncidentSeverityModerate IncidentSeverity = "moderate"
	IncidentSeverityMajor    IncidentSeverity = "major"
)

// IncidentSeverityValues lists every allowed IncidentSeverity.
var IncidentSeverityValues = []IncidentSeverity{IncidentSeverityMinor, IncidentSeverityModerate, IncidentSeverityMajor}

// Valid reports whether v is one of the allowed values.
func (v IncidentSeverity) Valid() bool {
	for _, allowed := range IncidentSeverityValues {
		if v == allowed {
			return true
		}
	}
	return false
}

// Label is a human-friendly name for v.
func (v IncidentSeverity) Label() string {
	text := strings.ReplaceAll(string(v), "_", " ")
	return strings.ToUpper(text[:1]) + text[1:]
}

// ParseIncidentSeverity turns text into a IncidentSeverity.
func ParseIncidentSeverity(text string) (IncidentSeverity, error) {
	v := IncidentSeverity(strings.ToLower(strings.TrimSpace(text)))
	if !v.Valid() {
		return "", Invalid("severity", "must be one of %s", IncidentSeverityList())
	}
	return v, nil
}

// IncidentSeverityList is every allowed value, comma separated.
func IncidentSeverityList() string {
	parts := make([]string, len(IncidentSeverityValues))
	for i, v := range IncidentSeverityValues {
		parts[i] = string(v)
	}
	return strings.Join(parts, ", ")
}

// NotificationChannel is the channel of a Notification.
type NotificationChannel string

// Allowed NotificationChannel values.
const (
	NotificationChannelEmail NotificationChannel = "email"
	NotificationChannelSms   NotificationChannel = "sms"
	NotificationChannelPush  NotificationChannel = "push"
)

// NotificationChannelValues lists every allowed NotificationChannel.
var NotificationChannelValues = []NotificationChannel{NotificationChannelEmail, NotificationChannelSms, NotificationChannelPush}

// Valid reports whether v is one of the allowed values.
func (v NotificationChannel) Valid() bool {
	for _, allowed := range NotificationChannelValues {
		if v == allowed {
			return true
		}
	}
	return false
}

// Label is a human-friendly name for v.
func (v NotificationChannel) Label() string {
	text := strings.ReplaceAll(string(v), "_", " ")
	return strings.ToUpper(text[:1]) + text[1:]
}

// ParseNotificationChannel turns text into a NotificationChannel.
func ParseNotificationChannel(text string) (NotificationChannel, error) {
	v := NotificationChannel(strings.ToLower(strings.TrimSpace(text)))
	if !v.Valid() {
		return "", Invalid("channel", "must be one of %s", NotificationChannelList())
	}
	return v, nil
}

// NotificationChannelList is every allowed value, comma separated.
func NotificationChannelList() string {
	parts := make([]string, len(NotificationChannelValues))
	for i, v := range NotificationChannelValues {
		parts[i] = string(v)
	}
	return strings.Join(parts, ", ")
}

// Vehicle is a vehicle record.
type Vehicle struct {
	ID      int         `json:"id"`
	Plate   string      `json:"plate"`
	Make    string      `json:"make"`
	Model   string      `json:"model"`
	Year    int         `json:"year"`
	Mileage int         `json:"mileage"`
	Fuel    VehicleFuel `json:"fuel"`
	Active  bool        `json:"active"`
}

// Validate checks every field and normalises text and amounts in place.
func (v *Vehicle) Validate() error {
	var err error
	if v.Plate, err = CheckText("plate", v.Plate, 120, true); err != nil {
		return err
	}
	if v.Make, err = CheckText("make", v.Make, 120, true); err != nil {
		return err
	}
	if v.Model, err = CheckText("model", v.Model, 120, true); err != nil {
		return err
	}
	if err = CheckInt("year", v.Year); err != nil {
		return err
	}
	if err = CheckInt("mileage", v.Mileage); err != nil {
		return err
	}
	if !v.Fuel.Valid() {
		return Invalid("fuel", "must be one of %s", VehicleFuelList())
	}
	return nil
}

// Summary is one line for logs and lists.
func (v Vehicle) Summary() string {
	return fmt.Sprintf("Vehicle #%d: %s", v.ID, v.Plate)
}

// Map is the record as plain values (for CSV export and templates).
func (v Vehicle) Map() map[string]any {
	return map[string]any{
		"id":      v.ID,
		"plate":   v.Plate,
		"make":    v.Make,
		"model":   v.Model,
		"year":    v.Year,
		"mileage": v.Mileage,
		"fuel":    string(v.Fuel),
		"active":  v.Active,
	}
}

// CompareVehicleByPlate orders vehicles by plate (for slices.SortFunc).
func CompareVehicleByPlate(a, b Vehicle) int {
	return cmp.Compare(a.Plate, b.Plate)
}

// CompareVehicleByMake orders vehicles by make (for slices.SortFunc).
func CompareVehicleByMake(a, b Vehicle) int {
	return cmp.Compare(a.Make, b.Make)
}

// CompareVehicleByModel orders vehicles by model (for slices.SortFunc).
func CompareVehicleByModel(a, b Vehicle) int {
	return cmp.Compare(a.Model, b.Model)
}

// CompareVehicleByYear orders vehicles by year (for slices.SortFunc).
func CompareVehicleByYear(a, b Vehicle) int {
	return cmp.Compare(a.Year, b.Year)
}

// CompareVehicleByMileage orders vehicles by mileage (for slices.SortFunc).
func CompareVehicleByMileage(a, b Vehicle) int {
	return cmp.Compare(a.Mileage, b.Mileage)
}

// CompareVehicleByFuel orders vehicles by fuel (for slices.SortFunc).
func CompareVehicleByFuel(a, b Vehicle) int {
	return cmp.Compare(string(a.Fuel), string(b.Fuel))
}

// VehiclePatch changes some fields of a Vehicle; nil means "leave as it is".
type VehiclePatch struct {
	Plate   *string      `json:"plate,omitempty"`
	Make    *string      `json:"make,omitempty"`
	Model   *string      `json:"model,omitempty"`
	Year    *int         `json:"year,omitempty"`
	Mileage *int         `json:"mileage,omitempty"`
	Fuel    *VehicleFuel `json:"fuel,omitempty"`
	Active  *bool        `json:"active,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p VehiclePatch) Apply(item Vehicle) (Vehicle, error) {
	if p.Plate != nil {
		item.Plate = *p.Plate
	}
	if p.Make != nil {
		item.Make = *p.Make
	}
	if p.Model != nil {
		item.Model = *p.Model
	}
	if p.Year != nil {
		item.Year = *p.Year
	}
	if p.Mileage != nil {
		item.Mileage = *p.Mileage
	}
	if p.Fuel != nil {
		item.Fuel = *p.Fuel
	}
	if p.Active != nil {
		item.Active = *p.Active
	}
	err := item.Validate()
	return item, err
}

// Driver is a driver record.
type Driver struct {
	ID            int     `json:"id"`
	Name          string  `json:"name"`
	Email         string  `json:"email"`
	LicenseNo     string  `json:"license_no"`
	LicenseExpiry string  `json:"license_expiry"`
	Rating        float64 `json:"rating"`
	OnDuty        bool    `json:"on_duty"`
}

// Validate checks every field and normalises text and amounts in place.
func (d *Driver) Validate() error {
	var err error
	if d.Name, err = CheckText("name", d.Name, 120, true); err != nil {
		return err
	}
	if d.Email, err = CheckEmail("email", d.Email); err != nil {
		return err
	}
	if d.LicenseNo, err = CheckText("license_no", d.LicenseNo, 120, true); err != nil {
		return err
	}
	if err = CheckDate("license_expiry", d.LicenseExpiry); err != nil {
		return err
	}
	if err = CheckNumber("rating", d.Rating); err != nil {
		return err
	}
	return nil
}

// Summary is one line for logs and lists.
func (d Driver) Summary() string {
	return fmt.Sprintf("Driver #%d: %s", d.ID, d.Name)
}

// Map is the record as plain values (for CSV export and templates).
func (d Driver) Map() map[string]any {
	return map[string]any{
		"id":             d.ID,
		"name":           d.Name,
		"email":          d.Email,
		"license_no":     d.LicenseNo,
		"license_expiry": d.LicenseExpiry,
		"rating":         d.Rating,
		"on_duty":        d.OnDuty,
	}
}

// CompareDriverByName orders drivers by name (for slices.SortFunc).
func CompareDriverByName(a, b Driver) int {
	return cmp.Compare(a.Name, b.Name)
}

// CompareDriverByEmail orders drivers by email (for slices.SortFunc).
func CompareDriverByEmail(a, b Driver) int {
	return cmp.Compare(a.Email, b.Email)
}

// CompareDriverByLicenseNo orders drivers by license no (for slices.SortFunc).
func CompareDriverByLicenseNo(a, b Driver) int {
	return cmp.Compare(a.LicenseNo, b.LicenseNo)
}

// CompareDriverByLicenseExpiry orders drivers by license expiry (for slices.SortFunc).
func CompareDriverByLicenseExpiry(a, b Driver) int {
	return cmp.Compare(a.LicenseExpiry, b.LicenseExpiry)
}

// CompareDriverByRating orders drivers by rating (for slices.SortFunc).
func CompareDriverByRating(a, b Driver) int {
	return cmp.Compare(a.Rating, b.Rating)
}

// DriverPatch changes some fields of a Driver; nil means "leave as it is".
type DriverPatch struct {
	Name          *string  `json:"name,omitempty"`
	Email         *string  `json:"email,omitempty"`
	LicenseNo     *string  `json:"license_no,omitempty"`
	LicenseExpiry *string  `json:"license_expiry,omitempty"`
	Rating        *float64 `json:"rating,omitempty"`
	OnDuty        *bool    `json:"on_duty,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p DriverPatch) Apply(item Driver) (Driver, error) {
	if p.Name != nil {
		item.Name = *p.Name
	}
	if p.Email != nil {
		item.Email = *p.Email
	}
	if p.LicenseNo != nil {
		item.LicenseNo = *p.LicenseNo
	}
	if p.LicenseExpiry != nil {
		item.LicenseExpiry = *p.LicenseExpiry
	}
	if p.Rating != nil {
		item.Rating = *p.Rating
	}
	if p.OnDuty != nil {
		item.OnDuty = *p.OnDuty
	}
	err := item.Validate()
	return item, err
}

// Trip is a trip record.
type Trip struct {
	ID         int        `json:"id"`
	VehicleID  int        `json:"vehicle_id"`
	DriverID   int        `json:"driver_id"`
	Started    string     `json:"started"`
	DistanceKm float64    `json:"distance_km"`
	Purpose    string     `json:"purpose"`
	Status     TripStatus `json:"status"`
}

// Validate checks every field and normalises text and amounts in place.
func (t *Trip) Validate() error {
	var err error
	if err = CheckRef("vehicle_id", t.VehicleID); err != nil {
		return err
	}
	if err = CheckRef("driver_id", t.DriverID); err != nil {
		return err
	}
	if err = CheckDate("started", t.Started); err != nil {
		return err
	}
	if err = CheckNumber("distance_km", t.DistanceKm); err != nil {
		return err
	}
	if t.Purpose, err = CheckText("purpose", t.Purpose, 120, true); err != nil {
		return err
	}
	if !t.Status.Valid() {
		return Invalid("status", "must be one of %s", TripStatusList())
	}
	return nil
}

// Summary is one line for logs and lists.
func (t Trip) Summary() string {
	return fmt.Sprintf("Trip #%d: %s", t.ID, t.Purpose)
}

// Map is the record as plain values (for CSV export and templates).
func (t Trip) Map() map[string]any {
	return map[string]any{
		"id":          t.ID,
		"vehicle_id":  t.VehicleID,
		"driver_id":   t.DriverID,
		"started":     t.Started,
		"distance_km": t.DistanceKm,
		"purpose":     t.Purpose,
		"status":      string(t.Status),
	}
}

// CompareTripByVehicleID orders trips by vehicle id (for slices.SortFunc).
func CompareTripByVehicleID(a, b Trip) int {
	return cmp.Compare(a.VehicleID, b.VehicleID)
}

// CompareTripByDriverID orders trips by driver id (for slices.SortFunc).
func CompareTripByDriverID(a, b Trip) int {
	return cmp.Compare(a.DriverID, b.DriverID)
}

// CompareTripByStarted orders trips by started (for slices.SortFunc).
func CompareTripByStarted(a, b Trip) int {
	return cmp.Compare(a.Started, b.Started)
}

// CompareTripByDistanceKm orders trips by distance km (for slices.SortFunc).
func CompareTripByDistanceKm(a, b Trip) int {
	return cmp.Compare(a.DistanceKm, b.DistanceKm)
}

// CompareTripByPurpose orders trips by purpose (for slices.SortFunc).
func CompareTripByPurpose(a, b Trip) int {
	return cmp.Compare(a.Purpose, b.Purpose)
}

// CompareTripByStatus orders trips by status (for slices.SortFunc).
func CompareTripByStatus(a, b Trip) int {
	return cmp.Compare(string(a.Status), string(b.Status))
}

// TripPatch changes some fields of a Trip; nil means "leave as it is".
type TripPatch struct {
	VehicleID  *int        `json:"vehicle_id,omitempty"`
	DriverID   *int        `json:"driver_id,omitempty"`
	Started    *string     `json:"started,omitempty"`
	DistanceKm *float64    `json:"distance_km,omitempty"`
	Purpose    *string     `json:"purpose,omitempty"`
	Status     *TripStatus `json:"status,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p TripPatch) Apply(item Trip) (Trip, error) {
	if p.VehicleID != nil {
		item.VehicleID = *p.VehicleID
	}
	if p.DriverID != nil {
		item.DriverID = *p.DriverID
	}
	if p.Started != nil {
		item.Started = *p.Started
	}
	if p.DistanceKm != nil {
		item.DistanceKm = *p.DistanceKm
	}
	if p.Purpose != nil {
		item.Purpose = *p.Purpose
	}
	if p.Status != nil {
		item.Status = *p.Status
	}
	err := item.Validate()
	return item, err
}

// FuelLog is a fuel log record.
type FuelLog struct {
	ID        int     `json:"id"`
	VehicleID int     `json:"vehicle_id"`
	Filled    string  `json:"filled"`
	Litres    float64 `json:"litres"`
	Cost      float64 `json:"cost"`
	Station   string  `json:"station"`
}

// Validate checks every field and normalises text and amounts in place.
func (f *FuelLog) Validate() error {
	var err error
	if err = CheckRef("vehicle_id", f.VehicleID); err != nil {
		return err
	}
	if err = CheckDate("filled", f.Filled); err != nil {
		return err
	}
	if err = CheckNumber("litres", f.Litres); err != nil {
		return err
	}
	if err = CheckNumber("cost", f.Cost); err != nil {
		return err
	}
	f.Cost = math.Round(f.Cost*100) / 100
	if f.Station, err = CheckText("station", f.Station, 120, true); err != nil {
		return err
	}
	return nil
}

// Summary is one line for logs and lists.
func (f FuelLog) Summary() string {
	return fmt.Sprintf("FuelLog #%d: %s", f.ID, f.Station)
}

// Map is the record as plain values (for CSV export and templates).
func (f FuelLog) Map() map[string]any {
	return map[string]any{
		"id":         f.ID,
		"vehicle_id": f.VehicleID,
		"filled":     f.Filled,
		"litres":     f.Litres,
		"cost":       f.Cost,
		"station":    f.Station,
	}
}

// CompareFuelLogByVehicleID orders fuel logs by vehicle id (for slices.SortFunc).
func CompareFuelLogByVehicleID(a, b FuelLog) int {
	return cmp.Compare(a.VehicleID, b.VehicleID)
}

// CompareFuelLogByFilled orders fuel logs by filled (for slices.SortFunc).
func CompareFuelLogByFilled(a, b FuelLog) int {
	return cmp.Compare(a.Filled, b.Filled)
}

// CompareFuelLogByLitres orders fuel logs by litres (for slices.SortFunc).
func CompareFuelLogByLitres(a, b FuelLog) int {
	return cmp.Compare(a.Litres, b.Litres)
}

// CompareFuelLogByCost orders fuel logs by cost (for slices.SortFunc).
func CompareFuelLogByCost(a, b FuelLog) int {
	return cmp.Compare(a.Cost, b.Cost)
}

// CompareFuelLogByStation orders fuel logs by station (for slices.SortFunc).
func CompareFuelLogByStation(a, b FuelLog) int {
	return cmp.Compare(a.Station, b.Station)
}

// FuelLogPatch changes some fields of a FuelLog; nil means "leave as it is".
type FuelLogPatch struct {
	VehicleID *int     `json:"vehicle_id,omitempty"`
	Filled    *string  `json:"filled,omitempty"`
	Litres    *float64 `json:"litres,omitempty"`
	Cost      *float64 `json:"cost,omitempty"`
	Station   *string  `json:"station,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p FuelLogPatch) Apply(item FuelLog) (FuelLog, error) {
	if p.VehicleID != nil {
		item.VehicleID = *p.VehicleID
	}
	if p.Filled != nil {
		item.Filled = *p.Filled
	}
	if p.Litres != nil {
		item.Litres = *p.Litres
	}
	if p.Cost != nil {
		item.Cost = *p.Cost
	}
	if p.Station != nil {
		item.Station = *p.Station
	}
	err := item.Validate()
	return item, err
}

// ServiceRecord is a service record record.
type ServiceRecord struct {
	ID        int               `json:"id"`
	VehicleID int               `json:"vehicle_id"`
	Serviced  string            `json:"serviced"`
	Odometer  int               `json:"odometer"`
	Cost      float64           `json:"cost"`
	Kind      ServiceRecordKind `json:"kind"`
	Notes     string            `json:"notes"`
}

// Validate checks every field and normalises text and amounts in place.
func (s *ServiceRecord) Validate() error {
	var err error
	if err = CheckRef("vehicle_id", s.VehicleID); err != nil {
		return err
	}
	if err = CheckDate("serviced", s.Serviced); err != nil {
		return err
	}
	if err = CheckInt("odometer", s.Odometer); err != nil {
		return err
	}
	if err = CheckNumber("cost", s.Cost); err != nil {
		return err
	}
	s.Cost = math.Round(s.Cost*100) / 100
	if !s.Kind.Valid() {
		return Invalid("kind", "must be one of %s", ServiceRecordKindList())
	}
	if s.Notes, err = CheckText("notes", s.Notes, 2000, false); err != nil {
		return err
	}
	return nil
}

// Summary is one line for logs and lists.
func (s ServiceRecord) Summary() string {
	return fmt.Sprintf("ServiceRecord #%d", s.ID)
}

// Map is the record as plain values (for CSV export and templates).
func (s ServiceRecord) Map() map[string]any {
	return map[string]any{
		"id":         s.ID,
		"vehicle_id": s.VehicleID,
		"serviced":   s.Serviced,
		"odometer":   s.Odometer,
		"cost":       s.Cost,
		"kind":       string(s.Kind),
		"notes":      s.Notes,
	}
}

// CompareServiceRecordByVehicleID orders service records by vehicle id (for slices.SortFunc).
func CompareServiceRecordByVehicleID(a, b ServiceRecord) int {
	return cmp.Compare(a.VehicleID, b.VehicleID)
}

// CompareServiceRecordByServiced orders service records by serviced (for slices.SortFunc).
func CompareServiceRecordByServiced(a, b ServiceRecord) int {
	return cmp.Compare(a.Serviced, b.Serviced)
}

// CompareServiceRecordByOdometer orders service records by odometer (for slices.SortFunc).
func CompareServiceRecordByOdometer(a, b ServiceRecord) int {
	return cmp.Compare(a.Odometer, b.Odometer)
}

// CompareServiceRecordByCost orders service records by cost (for slices.SortFunc).
func CompareServiceRecordByCost(a, b ServiceRecord) int {
	return cmp.Compare(a.Cost, b.Cost)
}

// CompareServiceRecordByKind orders service records by kind (for slices.SortFunc).
func CompareServiceRecordByKind(a, b ServiceRecord) int {
	return cmp.Compare(string(a.Kind), string(b.Kind))
}

// CompareServiceRecordByNotes orders service records by notes (for slices.SortFunc).
func CompareServiceRecordByNotes(a, b ServiceRecord) int {
	return cmp.Compare(a.Notes, b.Notes)
}

// ServiceRecordPatch changes some fields of a ServiceRecord; nil means "leave as it is".
type ServiceRecordPatch struct {
	VehicleID *int               `json:"vehicle_id,omitempty"`
	Serviced  *string            `json:"serviced,omitempty"`
	Odometer  *int               `json:"odometer,omitempty"`
	Cost      *float64           `json:"cost,omitempty"`
	Kind      *ServiceRecordKind `json:"kind,omitempty"`
	Notes     *string            `json:"notes,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p ServiceRecordPatch) Apply(item ServiceRecord) (ServiceRecord, error) {
	if p.VehicleID != nil {
		item.VehicleID = *p.VehicleID
	}
	if p.Serviced != nil {
		item.Serviced = *p.Serviced
	}
	if p.Odometer != nil {
		item.Odometer = *p.Odometer
	}
	if p.Cost != nil {
		item.Cost = *p.Cost
	}
	if p.Kind != nil {
		item.Kind = *p.Kind
	}
	if p.Notes != nil {
		item.Notes = *p.Notes
	}
	err := item.Validate()
	return item, err
}

// Incident is a incident record.
type Incident struct {
	ID         int              `json:"id"`
	VehicleID  int              `json:"vehicle_id"`
	DriverID   int              `json:"driver_id"`
	Happened   string           `json:"happened"`
	Severity   IncidentSeverity `json:"severity"`
	DamageCost float64          `json:"damage_cost"`
	Reported   bool             `json:"reported"`
}

// Validate checks every field and normalises text and amounts in place.
func (i *Incident) Validate() error {
	var err error
	if err = CheckRef("vehicle_id", i.VehicleID); err != nil {
		return err
	}
	if err = CheckRef("driver_id", i.DriverID); err != nil {
		return err
	}
	if err = CheckDate("happened", i.Happened); err != nil {
		return err
	}
	if !i.Severity.Valid() {
		return Invalid("severity", "must be one of %s", IncidentSeverityList())
	}
	if err = CheckNumber("damage_cost", i.DamageCost); err != nil {
		return err
	}
	i.DamageCost = math.Round(i.DamageCost*100) / 100
	return nil
}

// Summary is one line for logs and lists.
func (i Incident) Summary() string {
	return fmt.Sprintf("Incident #%d", i.ID)
}

// Map is the record as plain values (for CSV export and templates).
func (i Incident) Map() map[string]any {
	return map[string]any{
		"id":          i.ID,
		"vehicle_id":  i.VehicleID,
		"driver_id":   i.DriverID,
		"happened":    i.Happened,
		"severity":    string(i.Severity),
		"damage_cost": i.DamageCost,
		"reported":    i.Reported,
	}
}

// CompareIncidentByVehicleID orders incidents by vehicle id (for slices.SortFunc).
func CompareIncidentByVehicleID(a, b Incident) int {
	return cmp.Compare(a.VehicleID, b.VehicleID)
}

// CompareIncidentByDriverID orders incidents by driver id (for slices.SortFunc).
func CompareIncidentByDriverID(a, b Incident) int {
	return cmp.Compare(a.DriverID, b.DriverID)
}

// CompareIncidentByHappened orders incidents by happened (for slices.SortFunc).
func CompareIncidentByHappened(a, b Incident) int {
	return cmp.Compare(a.Happened, b.Happened)
}

// CompareIncidentBySeverity orders incidents by severity (for slices.SortFunc).
func CompareIncidentBySeverity(a, b Incident) int {
	return cmp.Compare(string(a.Severity), string(b.Severity))
}

// CompareIncidentByDamageCost orders incidents by damage cost (for slices.SortFunc).
func CompareIncidentByDamageCost(a, b Incident) int {
	return cmp.Compare(a.DamageCost, b.DamageCost)
}

// IncidentPatch changes some fields of a Incident; nil means "leave as it is".
type IncidentPatch struct {
	VehicleID  *int              `json:"vehicle_id,omitempty"`
	DriverID   *int              `json:"driver_id,omitempty"`
	Happened   *string           `json:"happened,omitempty"`
	Severity   *IncidentSeverity `json:"severity,omitempty"`
	DamageCost *float64          `json:"damage_cost,omitempty"`
	Reported   *bool             `json:"reported,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p IncidentPatch) Apply(item Incident) (Incident, error) {
	if p.VehicleID != nil {
		item.VehicleID = *p.VehicleID
	}
	if p.DriverID != nil {
		item.DriverID = *p.DriverID
	}
	if p.Happened != nil {
		item.Happened = *p.Happened
	}
	if p.Severity != nil {
		item.Severity = *p.Severity
	}
	if p.DamageCost != nil {
		item.DamageCost = *p.DamageCost
	}
	if p.Reported != nil {
		item.Reported = *p.Reported
	}
	err := item.Validate()
	return item, err
}

// Document is a document record.
type Document struct {
	ID        int    `json:"id"`
	VehicleID int    `json:"vehicle_id"`
	Title     string `json:"title"`
	Pages     int    `json:"pages"`
	Signed    bool   `json:"signed"`
	Version   int    `json:"version"`
	Issued    string `json:"issued"`
}

// Validate checks every field and normalises text and amounts in place.
func (d *Document) Validate() error {
	var err error
	if err = CheckRef("vehicle_id", d.VehicleID); err != nil {
		return err
	}
	if d.Title, err = CheckText("title", d.Title, 120, true); err != nil {
		return err
	}
	if err = CheckInt("pages", d.Pages); err != nil {
		return err
	}
	if err = CheckInt("version", d.Version); err != nil {
		return err
	}
	if err = CheckDate("issued", d.Issued); err != nil {
		return err
	}
	return nil
}

// Summary is one line for logs and lists.
func (d Document) Summary() string {
	return fmt.Sprintf("Document #%d: %s", d.ID, d.Title)
}

// Map is the record as plain values (for CSV export and templates).
func (d Document) Map() map[string]any {
	return map[string]any{
		"id":         d.ID,
		"vehicle_id": d.VehicleID,
		"title":      d.Title,
		"pages":      d.Pages,
		"signed":     d.Signed,
		"version":    d.Version,
		"issued":     d.Issued,
	}
}

// CompareDocumentByVehicleID orders documents by vehicle id (for slices.SortFunc).
func CompareDocumentByVehicleID(a, b Document) int {
	return cmp.Compare(a.VehicleID, b.VehicleID)
}

// CompareDocumentByTitle orders documents by title (for slices.SortFunc).
func CompareDocumentByTitle(a, b Document) int {
	return cmp.Compare(a.Title, b.Title)
}

// CompareDocumentByPages orders documents by pages (for slices.SortFunc).
func CompareDocumentByPages(a, b Document) int {
	return cmp.Compare(a.Pages, b.Pages)
}

// CompareDocumentByVersion orders documents by version (for slices.SortFunc).
func CompareDocumentByVersion(a, b Document) int {
	return cmp.Compare(a.Version, b.Version)
}

// CompareDocumentByIssued orders documents by issued (for slices.SortFunc).
func CompareDocumentByIssued(a, b Document) int {
	return cmp.Compare(a.Issued, b.Issued)
}

// DocumentPatch changes some fields of a Document; nil means "leave as it is".
type DocumentPatch struct {
	VehicleID *int    `json:"vehicle_id,omitempty"`
	Title     *string `json:"title,omitempty"`
	Pages     *int    `json:"pages,omitempty"`
	Signed    *bool   `json:"signed,omitempty"`
	Version   *int    `json:"version,omitempty"`
	Issued    *string `json:"issued,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p DocumentPatch) Apply(item Document) (Document, error) {
	if p.VehicleID != nil {
		item.VehicleID = *p.VehicleID
	}
	if p.Title != nil {
		item.Title = *p.Title
	}
	if p.Pages != nil {
		item.Pages = *p.Pages
	}
	if p.Signed != nil {
		item.Signed = *p.Signed
	}
	if p.Version != nil {
		item.Version = *p.Version
	}
	if p.Issued != nil {
		item.Issued = *p.Issued
	}
	err := item.Validate()
	return item, err
}

// Notification is a notification record.
type Notification struct {
	ID        int                 `json:"id"`
	Recipient string              `json:"recipient"`
	Title     string              `json:"title"`
	Sent      string              `json:"sent"`
	Channel   NotificationChannel `json:"channel"`
	Read      bool                `json:"read"`
}

// Validate checks every field and normalises text and amounts in place.
func (n *Notification) Validate() error {
	var err error
	if n.Recipient, err = CheckEmail("recipient", n.Recipient); err != nil {
		return err
	}
	if n.Title, err = CheckText("title", n.Title, 120, true); err != nil {
		return err
	}
	if err = CheckDate("sent", n.Sent); err != nil {
		return err
	}
	if !n.Channel.Valid() {
		return Invalid("channel", "must be one of %s", NotificationChannelList())
	}
	return nil
}

// Summary is one line for logs and lists.
func (n Notification) Summary() string {
	return fmt.Sprintf("Notification #%d: %s", n.ID, n.Recipient)
}

// Map is the record as plain values (for CSV export and templates).
func (n Notification) Map() map[string]any {
	return map[string]any{
		"id":        n.ID,
		"recipient": n.Recipient,
		"title":     n.Title,
		"sent":      n.Sent,
		"channel":   string(n.Channel),
		"read":      n.Read,
	}
}

// CompareNotificationByRecipient orders notifications by recipient (for slices.SortFunc).
func CompareNotificationByRecipient(a, b Notification) int {
	return cmp.Compare(a.Recipient, b.Recipient)
}

// CompareNotificationByTitle orders notifications by title (for slices.SortFunc).
func CompareNotificationByTitle(a, b Notification) int {
	return cmp.Compare(a.Title, b.Title)
}

// CompareNotificationBySent orders notifications by sent (for slices.SortFunc).
func CompareNotificationBySent(a, b Notification) int {
	return cmp.Compare(a.Sent, b.Sent)
}

// CompareNotificationByChannel orders notifications by channel (for slices.SortFunc).
func CompareNotificationByChannel(a, b Notification) int {
	return cmp.Compare(string(a.Channel), string(b.Channel))
}

// NotificationPatch changes some fields of a Notification; nil means "leave as it is".
type NotificationPatch struct {
	Recipient *string              `json:"recipient,omitempty"`
	Title     *string              `json:"title,omitempty"`
	Sent      *string              `json:"sent,omitempty"`
	Channel   *NotificationChannel `json:"channel,omitempty"`
	Read      *bool                `json:"read,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p NotificationPatch) Apply(item Notification) (Notification, error) {
	if p.Recipient != nil {
		item.Recipient = *p.Recipient
	}
	if p.Title != nil {
		item.Title = *p.Title
	}
	if p.Sent != nil {
		item.Sent = *p.Sent
	}
	if p.Channel != nil {
		item.Channel = *p.Channel
	}
	if p.Read != nil {
		item.Read = *p.Read
	}
	err := item.Validate()
	return item, err
}
