package model

import "strings"

// Valid reports whether v is one of the allowed values.
func (v ProductCategory) Valid() bool {
	for _, allowed := range ProductCategoryValues {
		if v == allowed {
			return true
		}
	}
	return false
}

// Label is a human-friendly name for v.
func (v ProductCategory) Label() string {
	text := strings.ReplaceAll(string(v), "_", " ")
	return strings.ToUpper(text[:1]) + text[1:]
}

// ParseProductCategory turns text into a ProductCategory.
func ParseProductCategory(text string) (ProductCategory, error) {
	v := ProductCategory(strings.ToLower(strings.TrimSpace(text)))
	if !v.Valid() {
		return "", Invalid("category", "must be one of %s", ProductCategoryList())
	}
	return v, nil
}

// ProductCategoryList is every allowed value, comma separated.
func ProductCategoryList() string {
	parts := make([]string, len(ProductCategoryValues))
	for i, v := range ProductCategoryValues {
		parts[i] = string(v)
	}
	return strings.Join(parts, ", ")
}
