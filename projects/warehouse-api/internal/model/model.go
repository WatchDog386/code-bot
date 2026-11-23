// Package model holds the Warehouse Inventory records and their validation rules.
package model

import (
	"errors"
	"fmt"
	"regexp"
)

var emailPattern = regexp.MustCompile(`^[^@\s]+@[^@\s]+\.[^@\s]+$`)

// ValidationError reports a field holding a value the service can't accept.
type ValidationError struct {
	Field   string
	Message string
}

func (e *ValidationError) Error() string { return e.Field + ": " + e.Message }

// Invalid builds a ValidationError.
func Invalid(field, format string, args ...any) error {
	return &ValidationError{Field: field, Message: fmt.Sprintf(format, args...)}
}

// IsValidation reports whether err is (or wraps) a ValidationError.
func IsValidation(err error) bool {
	var v *ValidationError
	return errors.As(err, &v)
}
