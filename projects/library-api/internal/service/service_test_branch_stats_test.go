package service_test

import "testing"

func TestBranchStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.BranchStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}
