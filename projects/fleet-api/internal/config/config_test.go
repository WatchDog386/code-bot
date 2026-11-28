package config

import "testing"

func from(values map[string]string) (Config, error) {
	return LoadFrom(func(key string) (string, bool) {
		v, ok := values[key]
		return v, ok
	})
}

func TestDefaults(t *testing.T) {
	got, err := from(map[string]string{})
	if err != nil || got != (Config{Host: "127.0.0.1", Port: 8080, SeedSize: 3}) {
		t.Fatalf("LoadFrom defaults = %+v, %v", got, err)
	}
}

func TestConfiguredValues(t *testing.T) {
	got, err := from(map[string]string{"FLEET_HOST": "0.0.0.0", "FLEET_PORT": "9090", "FLEET_SEED_SIZE": "0"})
	if err != nil || got != (Config{Host: "0.0.0.0", Port: 9090, SeedSize: 0}) {
		t.Fatalf("LoadFrom configured = %+v, %v", got, err)
	}
}

func TestInvalidPort(t *testing.T) {
	if _, err := from(map[string]string{"FLEET_PORT": "70000"}); err == nil {
		t.Fatal("expected an invalid port error")
	}
}
