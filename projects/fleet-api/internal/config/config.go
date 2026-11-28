// Package config loads validated process settings for the Fleet API.
package config

import (
	"fmt"
	"os"
	"strconv"
)

// Config contains listener and demo data settings.
type Config struct {
	Host     string
	Port     int
	SeedSize int
}

// Load reads settings from the process environment.
func Load() (Config, error) {
	return LoadFrom(os.LookupEnv)
}

// LoadFrom reads settings through lookup, which keeps parsing easy to test.
func LoadFrom(lookup func(string) (string, bool)) (Config, error) {
	host := value(lookup, "FLEET_HOST", "127.0.0.1")
	if host == "" {
		return Config{}, fmt.Errorf("FLEET_HOST must not be empty")
	}
	port, err := integer(lookup, "FLEET_PORT", 8080, 1, 65535)
	if err != nil {
		return Config{}, err
	}
	seedSize, err := integer(lookup, "FLEET_SEED_SIZE", 3, 0, 1000)
	if err != nil {
		return Config{}, err
	}
	return Config{Host: host, Port: port, SeedSize: seedSize}, nil
}

func value(lookup func(string) (string, bool), key, fallback string) string {
	if raw, ok := lookup(key); ok {
		return raw
	}
	return fallback
}

func integer(lookup func(string) (string, bool), key string, fallback, low, high int) (int, error) {
	raw := value(lookup, key, strconv.Itoa(fallback))
	n, err := strconv.Atoi(raw)
	if err != nil || n < low || n > high {
		return 0, fmt.Errorf("%s must be a whole number between %d and %d", key, low, high)
	}
	return n, nil
}
