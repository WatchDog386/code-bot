package model

import "strings"

// Valid reports whether v is one of the allowed values.
func (v BookGenre) Valid() bool {
	for _, allowed := range BookGenreValues {
		if v == allowed {
			return true
		}
	}
	return false
}

// Label is a human-friendly name for v.
func (v BookGenre) Label() string {
	text := strings.ReplaceAll(string(v), "_", " ")
	return strings.ToUpper(text[:1]) + text[1:]
}

// ParseBookGenre turns text into a BookGenre.
func ParseBookGenre(text string) (BookGenre, error) {
	v := BookGenre(strings.ToLower(strings.TrimSpace(text)))
	if !v.Valid() {
		return "", Invalid("genre", "must be one of %s", BookGenreList())
	}
	return v, nil
}

// BookGenreList is every allowed value, comma separated.
func BookGenreList() string {
	parts := make([]string, len(BookGenreValues))
	for i, v := range BookGenreValues {
		parts[i] = string(v)
	}
	return strings.Join(parts, ", ")
}
