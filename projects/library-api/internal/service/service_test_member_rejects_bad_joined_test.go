package service_test

import (
	"strings"
	"testing"

	"library-api/internal/service"
)

func TestMemberRejectsBadJoined(t *testing.T) {
	svc := seeded(t)
	item := service.SampleMember(12)
	item.Joined = "2026-02-30"
	_, err := svc.CreateMember(item)
	wantField(t, err, "joined")
}

func TestMemberRejectsBadTier(t *testing.T) {
	svc := seeded(t)
	item := service.SampleMember(12)
	item.Tier = "nope"
	_, err := svc.CreateMember(item)
	wantField(t, err, "tier")
}

func TestMemberRejectsBadFines(t *testing.T) {
	svc := seeded(t)
	item := service.SampleMember(12)
	item.Fines = -5
	_, err := svc.CreateMember(item)
	wantField(t, err, "fines")
}

func TestSearchMemberName(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetMember(2)
	for _, item := range svc.Members.SearchName(strings.ToUpper(target.Name)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Name)
}

func TestSearchMemberEmail(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetMember(2)
	for _, item := range svc.Members.SearchEmail(strings.ToUpper(target.Email)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Email)
}

func TestSearchMemberPhone(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetMember(2)
	for _, item := range svc.Members.SearchPhone(strings.ToUpper(target.Phone)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Phone)
}

func TestMemberJoinedRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SampleMember(2).Joined
	total := len(svc.Members.JoinedBefore(day)) + len(svc.Members.JoinedOn(day)) + len(svc.Members.JoinedAfter(day))
	if total != svc.Members.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.Members.Count())
	}
}
