package model

import (
	"fmt"
	"math"
)

// Validate checks every field and normalises text and amounts in place.
func (b *Book) Validate() error {
	var err error
	if b.Title, err = CheckText("title", b.Title, 120, true); err != nil {
		return err
	}
	if err = CheckRef("author_id", b.AuthorID); err != nil {
		return err
	}
	if b.Isbn, err = CheckText("isbn", b.Isbn, 120, true); err != nil {
		return err
	}
	if err = CheckInt("pages", b.Pages); err != nil {
		return err
	}
	if err = CheckNumber("price", b.Price); err != nil {
		return err
	}
	b.Price = math.Round(b.Price*100) / 100
	if err = CheckDate("published", b.Published); err != nil {
		return err
	}
	if !b.Genre.Valid() {
		return Invalid("genre", "must be one of %s", BookGenreList())
	}
	return nil
}

// Summary is one line for logs and lists.
func (b Book) Summary() string {
	return fmt.Sprintf("Book #%d: %s", b.ID, b.Title)
}
