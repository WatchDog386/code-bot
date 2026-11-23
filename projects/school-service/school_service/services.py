"""Services (continued)."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from .models import (
    ASSIGNMENT_FIELDS,
    ATTENDANCE_FIELDS,
    Assignment,
    Attendance,
    COURSE_FIELDS,
    Course,
    ENROLLMENT_FIELDS,
    Enrollment,
    STUDENT_FIELDS,
    Student,
    TEACHER_FIELDS,
    Teacher,
    ValidationError,
)
from .repository import (
    TeacherRepository,
    StudentRepository,
    CourseRepository,
    EnrollmentRepository,
    AssignmentRepository,
    AttendanceRepository,
)
from .services_sample_course import *  # noqa: F401,F403


class Services:
    """The whole service: storage plus one service object per model."""

    def __init__(self, store: Optional[Store] = None) -> None:
        self.store = store or Store()
        self.teachers = TeacherService(self.store)
        self.students = StudentService(self.store)
        self.courses = CourseService(self.store)
        self.enrollments = EnrollmentService(self.store)
        self.assignments = AssignmentService(self.store)
        self.attendances = AttendanceService(self.store)

    def seed(self, count: int = 3) -> None:
        """Fill every repository with `count` sample records."""
        for index in range(1, count + 1):
            self.teachers.create(sample_teacher(index))
            self.students.create(sample_student(index))
            self.courses.create(sample_course(index))
            self.enrollments.create(sample_enrollment(index))
            self.assignments.create(sample_assignment(index))
            self.attendances.create(sample_attendance(index))

    def summary(self) -> Dict[str, Any]:
        return {
            "teachers": self.teachers.stats(),
            "students": self.students.stats(),
            "courses": self.courses.stats(),
            "enrollments": self.enrollments.stats(),
            "assignments": self.assignments.stats(),
            "attendances": self.attendances.stats(),
        }
