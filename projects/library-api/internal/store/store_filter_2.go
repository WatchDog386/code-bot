package store

import (
	"strings"

	"library-api/internal/model"
)

// Filter returns the records keep() accepts, oldest first.
func (s *MemberStore) Filter(keep func(model.Member) bool) []model.Member {
	out := []model.Member{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// FindByName returns records whose name is exactly value.
func (s *MemberStore) FindByName(value string) []model.Member {
	return s.Filter(func(item model.Member) bool { return item.Name == value })
}

// SearchName returns records whose name contains text (any case).
func (s *MemberStore) SearchName(text string) []model.Member {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Member) bool { return strings.Contains(strings.ToLower(item.Name), needle) })
}

// FindByEmail returns records whose email is exactly value.
func (s *MemberStore) FindByEmail(value string) []model.Member {
	return s.Filter(func(item model.Member) bool { return item.Email == value })
}

// SearchEmail returns records whose email contains text (any case).
func (s *MemberStore) SearchEmail(text string) []model.Member {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Member) bool { return strings.Contains(strings.ToLower(item.Email), needle) })
}

// FindByPhone returns records whose phone is exactly value.
func (s *MemberStore) FindByPhone(value string) []model.Member {
	return s.Filter(func(item model.Member) bool { return item.Phone == value })
}

// SearchPhone returns records whose phone contains text (any case).
func (s *MemberStore) SearchPhone(text string) []model.Member {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Member) bool { return strings.Contains(strings.ToLower(item.Phone), needle) })
}

// JoinedBefore returns records whose joined is before day (YYYY-MM-DD).
func (s *MemberStore) JoinedBefore(day string) []model.Member {
	return s.Filter(func(item model.Member) bool { return item.Joined < day })
}

// JoinedAfter returns records whose joined is after day (YYYY-MM-DD).
func (s *MemberStore) JoinedAfter(day string) []model.Member {
	return s.Filter(func(item model.Member) bool { return item.Joined > day })
}

// JoinedOn returns records whose joined is day.
func (s *MemberStore) JoinedOn(day string) []model.Member {
	return s.Filter(func(item model.Member) bool { return item.Joined == day })
}

// WithTier returns records whose tier is value.
func (s *MemberStore) WithTier(value model.MemberTier) []model.Member {
	return s.Filter(func(item model.Member) bool { return item.Tier == value })
}
