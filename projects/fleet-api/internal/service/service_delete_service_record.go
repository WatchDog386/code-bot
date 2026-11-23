package service

import "fleet-api/internal/model"

// DeleteServiceRecord removes a service record nothing points at any more.
func (s *Service) DeleteServiceRecord(id int) error {
	if _, err := s.GetServiceRecord(id); err != nil {
		return err
	}
	s.ServiceRecords.Delete(id)
	return nil
}

// checkServiceRecordLinks makes sure every record a service record points at exists.
func (s *Service) checkServiceRecordLinks(item model.ServiceRecord) error {
	if _, ok := s.Vehicles.Get(item.VehicleID); !ok {
		return notFound("vehicle", item.VehicleID)
	}
	return nil
}

// AdjustServiceRecordOdometer adds delta to the odometer of a service record (it can't go below zero).
func (s *Service) AdjustServiceRecordOdometer(id int, delta int) (model.ServiceRecord, error) {
	item, err := s.GetServiceRecord(id)
	if err != nil {
		return model.ServiceRecord{}, err
	}
	value := item.Odometer + delta
	return s.UpdateServiceRecord(id, model.ServiceRecordPatch{Odometer: &value})
}
