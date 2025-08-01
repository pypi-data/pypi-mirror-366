from dataclasses import dataclass, field
from datetime import datetime


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


# @dataclass
# class TalentroApplication:
#     id: str
#     status: str
#     source: str
#     candidate: TalentroCandidate = field(default_factory=TalentroCandidate)
#     vacancy: TalentroVacancy = field(default_factory=TalentroVacancy)
#     created_at: datetime = field(default_factory=datetime.now)
#     updated_at: datetime = None