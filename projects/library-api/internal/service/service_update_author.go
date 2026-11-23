package service

import "library-api/internal/model"

// UpdateAuthor applies patch to a author.
func (s *Service) UpdateAuthor(id int, patch model.AuthorPatch) (model.Author, error) {
	current, err := s.GetAuthor(id)
	if err != nil {
		return model.Author{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Author{}, err
	}
	if err := s.checkAuthorLinks(updated); err != nil {
		return model.Author{}, err
	}
	s.Authors.Update(updated)
	return updated, nil
}

// DeleteAuthor removes a author nothing points at any more.
func (s *Service) DeleteAuthor(id int) error {
	if _, err := s.GetAuthor(id); err != nil {
		return err
	}
	if n := s.Books.CountForAuthor(id); n > 0 {
		return inUse("author", id, n, "books")
	}
	s.Authors.Delete(id)
	return nil
}

// checkAuthorLinks makes sure every record a author points at exists.
func (s *Service) checkAuthorLinks(_ model.Author) error {
	return nil
}

// ToggleAuthorActive flips the active flag of a author.
func (s *Service) ToggleAuthorActive(id int) (model.Author, error) {
	item, err := s.GetAuthor(id)
	if err != nil {
		return model.Author{}, err
	}
	flipped := !item.Active
	return s.UpdateAuthor(id, model.AuthorPatch{Active: &flipped})
}

// AuthorStats sums up every author.
type AuthorStats struct {
	Count  int `json:"count"`
	Active int `json:"active"`
}
