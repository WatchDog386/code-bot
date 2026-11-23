package store

import (
	"sort"
	"strings"
	"sync"

	"library-api/internal/model"
)

// CountByGenre counts records for every genre.
func (s *BookStore) CountByGenre() map[model.BookGenre]int {
	counts := map[model.BookGenre]int{}
	for _, v := range model.BookGenreValues {
		counts[v] = 0
	}
	for _, item := range s.List() {
		counts[item.Genre]++
	}
	return counts
}

// WhereAvailable returns records whose available flag equals flag.
func (s *BookStore) WhereAvailable(flag bool) []model.Book {
	return s.Filter(func(item model.Book) bool { return item.Available == flag })
}

// Search returns records where any text field contains text (any case).
func (s *BookStore) Search(text string) []model.Book {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Book) bool {
		for _, value := range []string{item.Title, item.Isbn} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// MemberStore keeps every member.
type MemberStore struct {
	mu     sync.RWMutex
	items  map[int]model.Member
	nextID int
}

// NewMemberStore returns an empty store.
func NewMemberStore() *MemberStore {
	return &MemberStore{items: map[int]model.Member{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *MemberStore) Create(item model.Member) model.Member {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *MemberStore) Get(id int) (model.Member, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *MemberStore) List() []model.Member {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.Member, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}
