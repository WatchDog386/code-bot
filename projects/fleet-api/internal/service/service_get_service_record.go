package service

import "fleet-api/internal/model"

// GetServiceRecord returns one service record.
func (s *Service) GetServiceRecord(id int) (model.ServiceRecord, error) {
	item, ok := s.ServiceRecords.Get(id)
	if !ok {
		return model.ServiceRecord{}, notFound("service record", id)
	}
	return item, nil
}

// ListServiceRecords returns every service record, oldest first.
func (s *Service) ListServiceRecords() []model.ServiceRecord {
	return s.ServiceRecords.List()
}

// UpdateServiceRecord applies patch to a service record.
func (s *Service) UpdateServiceRecord(id int, patch model.ServiceRecordPatch) (model.ServiceRecord, error) {
	current, err := s.GetServiceRecord(id)
	if err != nil {
		return model.ServiceRecord{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.ServiceRecord{}, err
	}
	if err := s.checkServiceRecordLinks(updated); err != nil {
		return model.ServiceRecord{}, err
	}
	s.ServiceRecords.Update(updated)
	return updated, nil
}
