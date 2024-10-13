from enum import Enum


class ParticipantType(Enum):
    PROFESSIONAL = 'PROFESSIONAL'
    STUDENT = "STUDENT"
    

class ParticipantStatus(Enum):
    PENDING = 'PENDING'
    SHORTLISTED = 'SHORTLISTED'
    CONFIRMED = 'CONFIRMED'
    ATTENDED = 'ATTENDED'