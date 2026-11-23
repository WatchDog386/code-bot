package model

import "strings"

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
