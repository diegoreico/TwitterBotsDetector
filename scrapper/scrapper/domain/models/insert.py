from typing import List
from pydantic import BaseModel
from etl.configuration.status import StatusCodes, status_messages


class InsertDocument(BaseModel):
    path: str
    file_type: str


class InsertRequest(BaseModel):
    documents: List[InsertDocument] = []


class InsertResult(BaseModel):
    status: int
    message: str

    class Builder:
        @staticmethod
        def dummy():
            return InsertResult(status=0, message="dummy")

        @staticmethod
        def long_operation():
            return InsertResult(status=StatusCodes.SLOW_TASK,
                                message=status_messages[StatusCodes.SLOW_TASK])

        @staticmethod
        def already_processing():
            return InsertResult(status=StatusCodes.ALREADY_PROCESSING,
                                message=status_messages[StatusCodes.ALREADY_PROCESSING])
