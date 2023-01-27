from datetime import datetime

from pydantic import BaseModel


class Error(BaseModel):
    responseError: str
    responseMessage: str
