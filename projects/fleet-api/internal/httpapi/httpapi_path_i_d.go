package httpapi

import (
	"net/http"
	"strconv"

	"fleet-api/internal/model"
)

func pathID(r *http.Request) (int, error) {
	id, err := strconv.Atoi(r.PathValue("id"))
	if err != nil || id < 1 {
		return 0, &model.ValidationError{Field: "id", Message: "must be a positive whole number"}
	}
	return id, nil
}

func queryInt(r *http.Request, name string) (int, bool, error) {
	raw := r.URL.Query().Get(name)
	if raw == "" {
		return 0, false, nil
	}
	v, err := strconv.Atoi(raw)
	if err != nil {
		return 0, false, &model.ValidationError{Field: name, Message: "must be a whole number"}
	}
	return v, true, nil
}

func queryFloat(r *http.Request, name string) (float64, bool, error) {
	raw := r.URL.Query().Get(name)
	if raw == "" {
		return 0, false, nil
	}
	v, err := strconv.ParseFloat(raw, 64)
	if err != nil {
		return 0, false, &model.ValidationError{Field: name, Message: "must be a number"}
	}
	return v, true, nil
}

func queryBool(r *http.Request, name string) (bool, bool, error) {
	raw := r.URL.Query().Get(name)
	if raw == "" {
		return false, false, nil
	}
	v, err := strconv.ParseBool(raw)
	if err != nil {
		return false, false, &model.ValidationError{Field: name, Message: "must be true or false"}
	}
	return v, true, nil
}
