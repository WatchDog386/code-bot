package service_test

import "testing"

func TestServiceRecordStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.ServiceRecordStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}
