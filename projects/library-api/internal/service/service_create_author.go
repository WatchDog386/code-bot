package service

import "library-api/internal/model"

// CreateAuthor validates and stores a new author.
func (s *Service) CreateAuthor(item model.Author) (model.Author, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Author{}, err
	}
	if err := s.checkAuthorLinks(item); err != nil {
		return model.Author{}, err
	}
	return s.Authors.Create(item), nil
}

// GetAuthor returns one author.
func (s *Service) GetAuthor(id int) (model.Author, error) {
	item, ok := s.Authors.Get(id)
	if !ok {
		return model.Author{}, notFound("author", id)
	}
	return item, nil
}

// ListAuthors returns every author, oldest first.
func (s *Service) ListAuthors() []model.Author {
	return s.Authors.List()
}
