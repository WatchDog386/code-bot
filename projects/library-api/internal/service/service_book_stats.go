package service

import (
	"fmt"
	"math"

	"library-api/internal/model"
)

// BookStats returns totals and breakdowns over every book.
func (s *Service) BookStats() BookStats {
	return BookStats{
		Count:        s.Books.Count(),
		TotalPages:   s.Books.TotalPages(),
		AveragePages: s.Books.AveragePages(),
		TotalPrice:   s.Books.TotalPrice(),
		AveragePrice: s.Books.AveragePrice(),
		ByGenre:      s.Books.CountByGenre(),
		Available:    len(s.Books.WhereAvailable(true)),
	}
}

// SampleBook returns valid data for a new book (links point at seeded records).
func SampleBook(i int) model.Book {
	return model.Book{
		Title:     fmt.Sprintf("Book title %d", i),
		AuthorID:  (i-1)%3 + 1,
		Isbn:      fmt.Sprintf("Book isbn %d", i),
		Pages:     i + 1,
		Price:     math.Round((10*float64(i)+0.99)*100) / 100,
		Published: fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		Genre:     model.BookGenreValues[i%5],
		Available: i%2 == 1,
	}
}

// CreateMember validates and stores a new member.
func (s *Service) CreateMember(item model.Member) (model.Member, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Member{}, err
	}
	if err := s.checkMemberLinks(item); err != nil {
		return model.Member{}, err
	}
	return s.Members.Create(item), nil
}

// GetMember returns one member.
func (s *Service) GetMember(id int) (model.Member, error) {
	item, ok := s.Members.Get(id)
	if !ok {
		return model.Member{}, notFound("member", id)
	}
	return item, nil
}
