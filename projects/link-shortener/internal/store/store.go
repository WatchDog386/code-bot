package store

import (
	"errors"
	"sync"
	"time"
)

var ErrNotFound = errors.New("link not found")
var ErrExists = errors.New("code already in use")

type Link struct {
	Code      string    `json:"code"`
	Target    string    `json:"target"`
	Hits      int64     `json:"hits"`
	CreatedAt time.Time `json:"created_at"`
	ExpiresAt time.Time `json:"expires_at,omitempty"`
}

func (l Link) Expired(now time.Time) bool {
	return !l.ExpiresAt.IsZero() && now.After(l.ExpiresAt)
}

type Store interface {
	Save(link Link) error
	Get(code string) (Link, error)
	IncrementHits(code string) error
	List() []Link
}

type MemoryStore struct {
	mu    sync.RWMutex
	links map[string]Link
}

func NewMemoryStore() *MemoryStore {
	return &MemoryStore{links: make(map[string]Link)}
}

func (s *MemoryStore) Save(link Link) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.links[link.Code]; ok {
		return ErrExists
	}
	s.links[link.Code] = link
	return nil
}

func (s *MemoryStore) Get(code string) (Link, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	link, ok := s.links[code]
	if !ok {
		return Link{}, ErrNotFound
	}
	return link, nil
}

func (s *MemoryStore) IncrementHits(code string) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	link, ok := s.links[code]
	if !ok {
		return ErrNotFound
	}
	link.Hits++
	s.links[code] = link
	return nil
}

func (s *MemoryStore) List() []Link {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]Link, 0, len(s.links))
	for _, l := range s.links {
		out = append(out, l)
	}
	return out
}
