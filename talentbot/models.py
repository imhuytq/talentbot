from datetime import datetime
from typing import List

from langchain.pydantic_v1 import BaseModel, EmailStr, Field
from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Location(BaseModel):
    address: str = Field(None, description="Address of the candidate")
    postal_code: str = Field(None, description="Postal code of the candidate")
    city: str = Field(None, description="City of the candidate")
    country_code: str = Field(None, description="Country code of the candidate")
    region: str = Field(None, description="Region of the candidate")


class Profile(BaseModel):
    network: str = Field(None, description="Name of the social network, e.g. LinkedIn")
    username: str = Field(None, description="Username of the candidate")
    url: str = Field(None, description="URL of the profile")


class Basics(BaseModel):
    name: str = Field(None, description="Name of the candidate")
    label: str = Field(None, description="Label of the candidate")
    image: str = Field(None, description="URL of the image")
    email: str = Field(None, description="Email of the candidate")
    phone: str = Field(None, description="Phone number of the candidate")
    url: str = Field(None, description="URL of the candidate")
    objective: str = Field(None, description="Objective of the candidate")
    location: Location = Field(None, description="Location of the candidate")
    profiles: List[Profile] = Field(
        None, description="Social profiles of the candidate"
    )


class WorkItem(BaseModel):
    name: str = Field(None, description="Name of the company")
    position: str = Field(None, description="Position of the candidate in the company")
    url: str = Field(None, description="URL of the company")
    start_date: str = Field(
        None, description="Start date of the work. Format: %b %Y (E.g. Jan 2020)"
    )
    end_date: str = Field(
        None,
        description="End date of the work. Format: %b %Y (E.g. Jan 2020), or 'Present'",
    )
    summary: str = Field(None, description="Summary of the work")
    highlights: List[str] = Field(None, description="Highlights of the work")


class VolunteerItem(BaseModel):
    organization: str = Field(None, description="Name of the organization")
    position: str = Field(
        None, description="Position of the candidate in the organization"
    )
    url: str = Field(None, description="URL of the organization")
    start_date: str = Field(
        None,
        description="Start date of the volunteer work. Format: %b %Y (E.g. Jan 2020)",
    )
    end_date: str = Field(
        None,
        description="End date of the volunteer work. Format: %b %Y (E.g. Jan 2020), or 'Present'",
    )
    summary: str = Field(None, description="Summary of the volunteer work")
    highlights: List[str] = Field(None, description="Highlights of the volunteer work")


class EducationItem(BaseModel):
    institution: str = Field(None, description="Name of the institution")
    url: str = Field(None, description="URL of the institution")
    area: str = Field(None, description="Area of study")
    study_type: str = Field(None, description="Type of study")
    start_date: str = Field(
        None, description="Start date of the education. Format: %b %Y (E.g. Jan 2020)"
    )
    end_date: str = Field(
        None,
        description="End date of the education. Format: %b %Y (E.g. Jan 2020), or 'Present'",
    )
    score: str = Field(None, description="Score of the education")
    courses: List[str] = Field(None, description="Courses taken during the education")


class Award(BaseModel):
    title: str = Field(None, description="Title of the award")
    date: str = Field(None, description="Date of the award")
    awarder: str = Field(None, description="Awarder of the award")
    summary: str = Field(None, description="Summary of the award")


class Certificate(BaseModel):
    name: str = Field(None, description="Name of the certificate")
    date: str = Field(None, description="Date of the certificate")
    issuer: str = Field(None, description="Issuer of the certificate")
    url: str = Field(None, description="URL of the certificate")


class Publication(BaseModel):
    name: str = Field(None, description="Name of the publication")
    publisher: str = Field(None, description="Publisher of the publication")
    release_date: str = Field(None, description="Release date of the publication")
    url: str = Field(None, description="URL of the publication")
    summary: str = Field(None, description="Summary of the publication")


class Skill(BaseModel):
    name: str = Field(None, description="Name of the skill")
    level: str = Field(None, description="Level of the skill")
    keywords: List[str] = Field(None, description="Keywords related to the skill")


class Language(BaseModel):
    language: str = Field(None, description="Name of the language")
    fluency: str = Field(None, description="Fluency level of the language")


class Interest(BaseModel):
    name: str = Field(None, description="Name of the interest")
    keywords: List[str] = Field(None, description="Keywords related to the interest")


class Reference(BaseModel):
    name: str = Field(None, description="Name of the reference")
    reference: str = Field(None, description="Reference")


class Project(BaseModel):
    name: str = Field(None, description="Name of the project")
    start_date: str = Field(
        None, description="Start date of the project. Format: %b %Y (E.g. Jan 2020)"
    )
    end_date: str = Field(
        None,
        description="End date of the project. Format: %b %Y (E.g. Jan 2020), or 'Present'",
    )
    description: str = Field(None, description="Description of the project")
    highlights: List[str] = Field(None, description="Highlights of the project")
    url: str = Field(None, description="URL of the project")


class Industry(BaseModel):
    name: str = Field(None, description="Name of the industry")
    confidence: float = Field(
        None, description="Confidence score of the prediction, 0-1"
    )


class Prediction(BaseModel):
    industries: List[Industry] = Field(None, description="Predicted industries")


class JsonResume(BaseModel):
    # basics: Basics = Field(description="Basic information")
    name: str = Field(None, description="Name of the candidate")
    gender: str = Field(None, description="Gender of the candidate")
    dob: str = Field(
        None,
        description="Date of birth of the candidate. Format: %Y-%m-%d (E.g. 1990-01-01)",
    )
    label: str = Field(None, description="Label of the candidate")
    image: str = Field(None, description="URL of the image")
    email: EmailStr = Field(None, description="Email of the candidate")
    phone: str = Field(None, description="Phone number of the candidate")
    url: str = Field(None, description="URL of the candidate")
    objective: str = Field(None, description="Objective of the candidate")
    location: Location = Field(None, description="Location of the candidate")
    profiles: List[Profile] = Field(
        None, description="Social profiles of the candidate"
    )
    work: List[WorkItem] = Field([], description="Work experience")
    volunteer: List[VolunteerItem] = Field([], description="Volunteer experience")
    education: List[EducationItem] = Field([], description="Education")
    awards: List[Award] = Field([], description="Awards")
    certificates: List[Certificate] = Field([], description="Certificates")
    publications: List[Publication] = Field([], description="Publications")
    skills: List[Skill] = Field([], description="Skills")
    languages: List[Language] = Field([], description="Languages")
    interests: List[Interest] = Field([], description="Interests")
    references: List[Reference] = Field([], description="References")
    projects: List[Project] = Field([], description="Projects")
    prediction: Prediction = Field(description="Prediction of suitable industries")


class Base(DeclarativeBase):
    pass


class Resume(Base):
    __tablename__ = "resumes"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    # email is unique
    email: Mapped[str] = mapped_column(String(256), unique=True)
    cv_file: Mapped[str] = mapped_column(String(256))
    # data is jsonb
    data: Mapped[dict] = mapped_column(JSON())
    summary: Mapped[str] = mapped_column(String())
    industries: Mapped[List["ResumeIndustry"]] = relationship(
        back_populates="resume", cascade="all, delete-orphan"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"Resume(id={self.id!r}, name={self.name!r}, email={self.email!r})"


class ResumeIndustry(Base):
    __tablename__ = "resume_industry"
    id: Mapped[int] = mapped_column(primary_key=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"))
    resume: Mapped["Resume"] = relationship(back_populates="industries")
    industry: Mapped[str] = mapped_column(String(256))
    confidence: Mapped[float] = mapped_column(Float)

    def __repr__(self) -> str:
        return f"ResumeIndustry(id={self.id!r}, resume_id={self.resume_id!r}, industry={self.industry!r}, confidence={self.confidence!r})"
