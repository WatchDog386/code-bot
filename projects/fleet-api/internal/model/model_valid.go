package model

import "strings"

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
