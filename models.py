"""Pydantic models and validation rules for student records."""
from typing import Literal, Self
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator


class Course(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    name: str = Field(min_length=1)
    marks: float = Field(ge=0, le=100)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Course name must not be blank")
        return value


class Student(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1)
    student_id: str = Field(pattern=r"^S[0-9]+$")
    credits_completed: int = Field(default=0, ge=0, strict=True)
    credits_required: int = Field(default=120, gt=0, strict=True)
    courses: list[Course] = Field(min_length=1)

    @field_validator("name", "student_id")
    @classmethod
    def clean_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value must not be blank")
        return value

    @field_validator("courses")
    @classmethod
    def unique_courses(cls, courses: list[Course]) -> list[Course]:
        names = [course.name.casefold() for course in courses]
        if len(names) != len(set(names)):
            raise ValueError("Course names must be unique (case-insensitive)")
        return courses

    @model_validator(mode="after")
    def check_credits(self) -> Self:
        if self.credits_completed > self.credits_required:
            raise ValueError("Completed credits cannot exceed required credits")
        return self

    @computed_field
    @property
    def average_marks(self) -> float:
        return round(sum(course.marks for course in self.courses) / len(self.courses), 2)

    @computed_field
    @property
    def result(self) -> Literal["PASS", "FAIL"]:
        return "PASS" if all(course.marks >= 40 for course in self.courses) else "FAIL"
