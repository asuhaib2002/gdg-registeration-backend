from enum import Enum


class ParticipantType(Enum):
    PROFESSIONAL = "PROFESSIONAL"
    STUDENT = "STUDENT"


class ParticipantStatus(Enum):
    PENDING = "PENDING"
    SHORTLISTED = "SHORTLISTED"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    ATTENDED = "ATTENDED"

    @classmethod
    def is_valid_status(cls, status):
        """
        Check if the provided status is a valid enum value.

        Args:
            status (str): The status to validate.

        Returns:
            bool: True if the status is valid, False otherwise.
        """
        return status in cls._value2member_map_
