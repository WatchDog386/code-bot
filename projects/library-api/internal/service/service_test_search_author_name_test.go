package service_test

import (
	"strings"
	"testing"
)

func TestSearchAuthorName(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetAuthor(2)
	for _, item := range svc.Authors.SearchName(strings.ToUpper(target.Name)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Name)
}

func TestSearchAuthorEmail(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetAuthor(2)
	for _, item := range svc.Authors.SearchEmail(strings.ToUpper(target.Email)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Email)
}
