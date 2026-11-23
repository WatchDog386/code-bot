package httpapi

import (
	"encoding/json"
	"net/http"
	"strconv"

	"warehouse-api/internal/model"
)

func decode(r *http.Request, into any) error {
	dec := json.NewDecoder(r.Body)
	dec.DisallowUnknownFields()
	if err := dec.Decode(into); err != nil {
		return &model.ValidationError{Field: "body", Message: err.Error()}
	}
	return nil
}

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
