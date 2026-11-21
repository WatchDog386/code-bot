package shortener

import (
	"crypto/rand"
	"errors"
	"math/big"
	"net/url"
	"strings"
	"time"

	"github.com/example/link-shortener/internal/store"
)

const alphabet = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"

var ErrInvalidURL = errors.New("invalid url")

type Service struct {
	store      store.Store
	codeLength int
	now        func() time.Time
}

func New(s store.Store, codeLength int) *Service {
	return &Service{store: s, codeLength: codeLength, now: time.Now}
}

func (s *Service) Shorten(target string, ttl time.Duration) (store.Link, error) {
	if err := validate(target); err != nil {
		return store.Link{}, err
	}

	for attempt := 0; attempt < 5; attempt++ {
		code, err := randomCode(s.codeLength)
		if err != nil {
			return store.Link{}, err
		}

		link := store.Link{
			Code:      code,
			Target:    target,
			CreatedAt: s.now(),
		}
		if ttl > 0 {
			link.ExpiresAt = link.CreatedAt.Add(ttl)
		}

		err = s.store.Save(link)
		if errors.Is(err, store.ErrExists) {
			continue
		}
		return link, err
	}
	return store.Link{}, errors.New("could not generate a unique code")
}

func (s *Service) Resolve(code string) (string, error) {
	link, err := s.store.Get(code)
	if err != nil {
		return "", err
	}
	if link.Expired(s.now()) {
		return "", store.ErrNotFound
	}
	_ = s.store.IncrementHits(code)
	return link.Target, nil
}

func validate(raw string) error {
	u, err := url.ParseRequestURI(strings.TrimSpace(raw))
	if err != nil || u.Host == "" {
		return ErrInvalidURL
	}
	if u.Scheme != "http" && u.Scheme != "https" {
		return ErrInvalidURL
	}
	return nil
}

func randomCode(n int) (string, error) {
	var b strings.Builder
	max := big.NewInt(int64(len(alphabet)))
	for i := 0; i < n; i++ {
		idx, err := rand.Int(rand.Reader, max)
		if err != nil {
			return "", err
		}
		b.WriteByte(alphabet[idx.Int64()])
	}
	return b.String(), nil
}
