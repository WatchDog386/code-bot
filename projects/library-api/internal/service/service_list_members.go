package service

import "library-api/internal/model"

// ListMembers returns every member, oldest first.
func (s *Service) ListMembers() []model.Member {
	return s.Members.List()
}

// UpdateMember applies patch to a member.
func (s *Service) UpdateMember(id int, patch model.MemberPatch) (model.Member, error) {
	current, err := s.GetMember(id)
	if err != nil {
		return model.Member{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Member{}, err
	}
	if err := s.checkMemberLinks(updated); err != nil {
		return model.Member{}, err
	}
	s.Members.Update(updated)
	return updated, nil
}

// DeleteMember removes a member nothing points at any more.
func (s *Service) DeleteMember(id int) error {
	if _, err := s.GetMember(id); err != nil {
		return err
	}
	if n := s.Loans.CountForMember(id); n > 0 {
		return inUse("member", id, n, "loans")
	}
	if n := s.Reservations.CountForMember(id); n > 0 {
		return inUse("member", id, n, "reservations")
	}
	s.Members.Delete(id)
	return nil
}
