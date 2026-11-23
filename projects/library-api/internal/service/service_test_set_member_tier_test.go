package service_test

import (
	"errors"
	"testing"

	"library-api/internal/model"
	"library-api/internal/service"
)

func TestSetMemberTier(t *testing.T) {
	svc := seeded(t)
	last := model.MemberTierValues[len(model.MemberTierValues)-1]
	item, err := svc.SetMemberTier(1, last)
	if err != nil || item.Tier != last {
		t.Fatalf("set = %v, %v", item.Tier, err)
	}
	if got, want := svc.Members.CountByTier()[last], len(svc.Members.WithTier(last)); got != want {
		t.Fatalf("count %d != %d", got, want)
	}
}

func TestAdjustMemberFines(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetMember(1)
	after, err := svc.AdjustMemberFines(1, 1.5)
	if err != nil || after.Fines-before.Fines < 1.49 || after.Fines-before.Fines > 1.51 {
		t.Fatalf("adjust = %v, %v", after.Fines, err)
	}
}

func TestToggleMemberActive(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetMember(1)
	after, err := svc.ToggleMemberActive(1)
	if err != nil || after.Active == before.Active {
		t.Fatalf("toggle = %v, %v", after.Active, err)
	}
}

func TestDeleteMember(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateMember(service.SampleMember(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteMember(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetMember(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestDeleteMemberInUse(t *testing.T) {
	svc := seeded(t)
	if err := svc.DeleteMember(1); !errors.Is(err, service.ErrConflict) {
		t.Fatalf("want ErrConflict, got %v", err)
	}
}

func TestMemberStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.MemberStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}
