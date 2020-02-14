from typing import List
from pydantic import BaseModel

class AbsenceType(BaseModel):
    type: str
    dec_threshold: int

    @staticmethod
    def is_dummy(contract):
        return 0

    @staticmethod
    def dummy():
        return AbsenceType(
            type='dummy',
            dec_threshold=123
        )

    @staticmethod
    def from_tuple(row):

        return AbsenceType(
            type='dummy',
            dec_threshold=123
        )
