# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .error import Error
from .._models import BaseModel
from .answer_response import AnswerResponse

__all__ = ["APIResponseListAnswers"]


class APIResponseListAnswers(BaseModel):
    data: Optional[List[AnswerResponse]] = None
    """The primary response payload. Contains the result of the request if successful."""

    errors: Optional[List[Error]] = None
    """List of structured error messages, if any occurred during the request."""
