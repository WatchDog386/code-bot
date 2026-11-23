package model

import "cmp"

// CompareAuthorByCountry orders authors by country (for slices.SortFunc).
func CompareAuthorByCountry(a, b Author) int {
	return cmp.Compare(a.Country, b.Country)
}

// CompareAuthorByBorn orders authors by born (for slices.SortFunc).
func CompareAuthorByBorn(a, b Author) int {
	return cmp.Compare(a.Born, b.Born)
}

// AuthorPatch changes some fields of a Author; nil means "leave as it is".
type AuthorPatch struct {
	Name    *string `json:"name,omitempty"`
	Email   *string `json:"email,omitempty"`
	Country *string `json:"country,omitempty"`
	Born    *string `json:"born,omitempty"`
	Active  *bool   `json:"active,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p AuthorPatch) Apply(item Author) (Author, error) {
	if p.Name != nil {
		item.Name = *p.Name
	}
	if p.Email != nil {
		item.Email = *p.Email
	}
	if p.Country != nil {
		item.Country = *p.Country
	}
	if p.Born != nil {
		item.Born = *p.Born
	}
	if p.Active != nil {
		item.Active = *p.Active
	}
	err := item.Validate()
	return item, err
}

// Book is a book record.
type Book struct {
	ID        int       `json:"id"`
	Title     string    `json:"title"`
	AuthorID  int       `json:"author_id"`
	Isbn      string    `json:"isbn"`
	Pages     int       `json:"pages"`
	Price     float64   `json:"price"`
	Published string    `json:"published"`
	Genre     BookGenre `json:"genre"`
	Available bool      `json:"available"`
}
