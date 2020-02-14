from typing import List
from pydantic import BaseModel

class Status(BaseModel):
    project_name: str
    host: str
    port: int
    api_endpoint: str
    cors_origins: str