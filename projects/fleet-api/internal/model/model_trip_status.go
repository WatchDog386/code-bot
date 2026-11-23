package model

import "strings"

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
