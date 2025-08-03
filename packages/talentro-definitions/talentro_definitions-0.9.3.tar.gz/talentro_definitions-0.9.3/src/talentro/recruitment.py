from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class TalentroVacancyLocation:
    #  Required fields
    zip_code: str
    city: str

    # Optional fields
    address: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None


@dataclass
class TalentroSalary:
    min: float = 0.0
    max: float = 0.0
    currency: str = "EUR"
    interval: str = "Month"


@dataclass
class TalentroHours:
    min: int = 0
    max: int = 40
    fte: float = 1.0


@dataclass
class TalentroContactDetails:

    # Required fields
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[str] = None


@dataclass
class TalentroCandidate:
    id: str
    email: str = ""
    first_name: str = ""
    last_name: str = ""
    phone_number: str = ""
    hashed_email: str = ""
    cv: str = ""
    motivation_letter: str = ""
    linked_in: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = None


@dataclass
class TalentroVacancy:

    # Required fields
    reference_number: str
    requisition_id: str
    title: str
    description: str
    job_site_url: str
    company_name: str
    publish_date: datetime
    category: List[str] = field(default_factory=list)
    experience: List[str] = field(default_factory=list)
    education: List[str] = field(default_factory=list)

    # Connected data
    hours: TalentroHours = field(default_factory=TalentroHours)
    location: TalentroVacancyLocation = field(default_factory=TalentroVacancyLocation)
    salary: TalentroSalary = field(default_factory=TalentroSalary)
    recruiter: TalentroContactDetails = field(default_factory=TalentroContactDetails)

    # Optional fields
    status: Optional[str] = None
    parent_company_name: Optional[str] = None
    remote_type: Optional[str] = None
    expiration_date: Optional[datetime] = None
    last_updated_date: Optional[datetime] = None

@dataclass
class TalentroApplication:
    id: str
    status: str
    source: str
    candidate: TalentroCandidate = field(default_factory=TalentroCandidate)
    vacancy: TalentroVacancy = field(default_factory=TalentroVacancy)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = None