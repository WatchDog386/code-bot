package service_test

import "testing"

func TestReservationStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.ReservationStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}
