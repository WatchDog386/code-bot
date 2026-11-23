package service

import (
	"fmt"

	"library-api/internal/model"
)

// AuthorStats returns totals and breakdowns over every author.
func (s *Service) AuthorStats() AuthorStats {
	return AuthorStats{
		Count:  s.Authors.Count(),
		Active: len(s.Authors.WhereActive(true)),
	}
}

// SampleAuthor returns valid data for a new author (links point at seeded records).
func SampleAuthor(i int) model.Author {
	return model.Author{
		Name:    fmt.Sprintf("Author name %d", i),
		Email:   fmt.Sprintf("author%d@example.com", i),
		Country: fmt.Sprintf("Author country %d", i),
		Born:    fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		Active:  i%2 == 1,
	}
}

// CreateBook validates and stores a new book.
func (s *Service) CreateBook(item model.Book) (model.Book, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Book{}, err
	}
	if err := s.checkBookLinks(item); err != nil {
		return model.Book{}, err
	}
	return s.Books.Create(item), nil
}

// GetBook returns one book.
func (s *Service) GetBook(id int) (model.Book, error) {
	item, ok := s.Books.Get(id)
	if !ok {
		return model.Book{}, notFound("book", id)
	}
	return item, nil
}

// ListBooks returns every book, oldest first.
func (s *Service) ListBooks() []model.Book {
	return s.Books.List()
}

// UpdateBook applies patch to a book.
func (s *Service) UpdateBook(id int, patch model.BookPatch) (model.Book, error) {
	current, err := s.GetBook(id)
	if err != nil {
		return model.Book{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Book{}, err
	}
	if err := s.checkBookLinks(updated); err != nil {
		return model.Book{}, err
	}
	s.Books.Update(updated)
	return updated, nil
}

// DeleteBook removes a book nothing points at any more.
func (s *Service) DeleteBook(id int) error {
	if _, err := s.GetBook(id); err != nil {
		return err
	}
	if n := s.Loans.CountForBook(id); n > 0 {
		return inUse("book", id, n, "loans")
	}
	if n := s.Reservations.CountForBook(id); n > 0 {
		return inUse("book", id, n, "reservations")
	}
	s.Books.Delete(id)
	return nil
}

// checkBookLinks makes sure every record a book points at exists.
func (s *Service) checkBookLinks(item model.Book) error {
	if _, ok := s.Authors.Get(item.AuthorID); !ok {
		return notFound("author", item.AuthorID)
	}
	return nil
}
