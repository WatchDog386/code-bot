package model

import (
	"strings"
	"time"
)

// CheckText trims value and checks it isn't empty (unless optional) or too long.
func CheckText(field, value string, max int, required bool) (string, error) {
	cleaned := strings.TrimSpace(value)
	if required && cleaned == "" {
		return "", Invalid(field, "is required")
	}
	if len(cleaned) > max {
		return "", Invalid(field, "must be at most %d characters", max)
	}
	return cleaned, nil
}

// CheckEmail checks for a plausible e-mail address and lower-cases it.
func CheckEmail(field, value string) (string, error) {
	text, err := CheckText(field, value, 254, true)
	if err != nil {
		return "", err
	}
	if !emailPattern.MatchString(text) {
		return "", Invalid(field, "must be an e-mail address")
	}
	return strings.ToLower(text), nil
}

// CheckInt rejects negative numbers.
func CheckInt(field string, value int) error {
	if value < 0 {
		return Invalid(field, "must be at least 0")
	}
	if value > 1_000_000_000 {
		return Invalid(field, "must be at most 1000000000")
	}
	return nil
}

// CheckNumber rejects negative amounts.
func CheckNumber(field string, value float64) error {
	if value < 0 {
		return Invalid(field, "must be at least 0")
	}
	return nil
}

// CheckDate wants an ISO date (YYYY-MM-DD) that exists in the calendar.
func CheckDate(field, value string) error {
	if _, err := time.Parse("2006-01-02", value); err != nil {
		return Invalid(field, "must be a real date like 2026-01-31")
	}
	return nil
}

// CheckRef wants the id of another record (existence is checked by the service).
func CheckRef(field string, value int) error {
	if value < 1 {
		return Invalid(field, "must point at a record")
	}
	return nil
}

// BookGenre is the genre of a Book.
type BookGenre string

// Allowed BookGenre values.
const (
	BookGenreFiction  BookGenre = "fiction"
	BookGenreScience  BookGenre = "science"
	BookGenreHistory  BookGenre = "history"
	BookGenrePoetry   BookGenre = "poetry"
	BookGenreChildren BookGenre = "children"
)

// BookGenreValues lists every allowed BookGenre.
var BookGenreValues = []BookGenre{BookGenreFiction, BookGenreScience, BookGenreHistory, BookGenrePoetry, BookGenreChildren}
