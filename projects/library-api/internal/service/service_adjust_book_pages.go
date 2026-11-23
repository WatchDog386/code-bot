package service

import (
	"math"

	"library-api/internal/model"
)

// AdjustBookPages adds delta to the pages of a book (it can't go below zero).
func (s *Service) AdjustBookPages(id int, delta int) (model.Book, error) {
	item, err := s.GetBook(id)
	if err != nil {
		return model.Book{}, err
	}
	value := item.Pages + delta
	return s.UpdateBook(id, model.BookPatch{Pages: &value})
}

// AdjustBookPrice adds delta to the price of a book (it can't go below zero).
func (s *Service) AdjustBookPrice(id int, delta float64) (model.Book, error) {
	item, err := s.GetBook(id)
	if err != nil {
		return model.Book{}, err
	}
	value := math.Round((item.Price+delta)*100) / 100
	return s.UpdateBook(id, model.BookPatch{Price: &value})
}

// SetBookGenre moves a book to another genre.
func (s *Service) SetBookGenre(id int, value model.BookGenre) (model.Book, error) {
	return s.UpdateBook(id, model.BookPatch{Genre: &value})
}

// ToggleBookAvailable flips the available flag of a book.
func (s *Service) ToggleBookAvailable(id int) (model.Book, error) {
	item, err := s.GetBook(id)
	if err != nil {
		return model.Book{}, err
	}
	flipped := !item.Available
	return s.UpdateBook(id, model.BookPatch{Available: &flipped})
}

// BookStats sums up every book.
type BookStats struct {
	Count        int                     `json:"count"`
	TotalPages   int                     `json:"total_pages"`
	AveragePages float64                 `json:"average_pages"`
	TotalPrice   float64                 `json:"total_price"`
	AveragePrice float64                 `json:"average_price"`
	ByGenre      map[model.BookGenre]int `json:"by_genre"`
	Available    int                     `json:"available"`
}
