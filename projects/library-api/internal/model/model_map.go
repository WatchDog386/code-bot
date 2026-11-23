package model

import "cmp"

// Map is the record as plain values (for CSV export and templates).
func (b Book) Map() map[string]any {
	return map[string]any{
		"id":        b.ID,
		"title":     b.Title,
		"author_id": b.AuthorID,
		"isbn":      b.Isbn,
		"pages":     b.Pages,
		"price":     b.Price,
		"published": b.Published,
		"genre":     string(b.Genre),
		"available": b.Available,
	}
}

// CompareBookByTitle orders books by title (for slices.SortFunc).
func CompareBookByTitle(a, b Book) int {
	return cmp.Compare(a.Title, b.Title)
}

// CompareBookByAuthorID orders books by author id (for slices.SortFunc).
func CompareBookByAuthorID(a, b Book) int {
	return cmp.Compare(a.AuthorID, b.AuthorID)
}

// CompareBookByIsbn orders books by isbn (for slices.SortFunc).
func CompareBookByIsbn(a, b Book) int {
	return cmp.Compare(a.Isbn, b.Isbn)
}

// CompareBookByPages orders books by pages (for slices.SortFunc).
func CompareBookByPages(a, b Book) int {
	return cmp.Compare(a.Pages, b.Pages)
}

// CompareBookByPrice orders books by price (for slices.SortFunc).
func CompareBookByPrice(a, b Book) int {
	return cmp.Compare(a.Price, b.Price)
}

// CompareBookByPublished orders books by published (for slices.SortFunc).
func CompareBookByPublished(a, b Book) int {
	return cmp.Compare(a.Published, b.Published)
}

// CompareBookByGenre orders books by genre (for slices.SortFunc).
func CompareBookByGenre(a, b Book) int {
	return cmp.Compare(string(a.Genre), string(b.Genre))
}

// BookPatch changes some fields of a Book; nil means "leave as it is".
type BookPatch struct {
	Title     *string    `json:"title,omitempty"`
	AuthorID  *int       `json:"author_id,omitempty"`
	Isbn      *string    `json:"isbn,omitempty"`
	Pages     *int       `json:"pages,omitempty"`
	Price     *float64   `json:"price,omitempty"`
	Published *string    `json:"published,omitempty"`
	Genre     *BookGenre `json:"genre,omitempty"`
	Available *bool      `json:"available,omitempty"`
}
