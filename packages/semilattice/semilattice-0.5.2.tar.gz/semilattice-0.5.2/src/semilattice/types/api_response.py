# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .error import Error
from .._models import BaseModel

__all__ = ["APIResponse", "Data"]


class Data(BaseModel):
    id: str
    """Unique identifier for the population"""

    created_at: datetime
    """Population creation timestamp"""

    name: str
    """Name of the population"""

    public: bool
    """Whether the population is public"""

    question_count: int
    """Total number of questions"""

    simulacrum_count: int
    """Total number of simulacra"""

    status: str
    """Current status of the population"""

    avg_mean_absolute_error: Optional[float] = None
    """Average Mean Absolute Error across all benchmark generations"""

    avg_mean_squared_error: Optional[float] = None
    """Average Mean Squared Error across all benchmark generations"""

    avg_normalised_kullback_leibler_divergence: Optional[float] = None
    """Average normalised KL divergence across all benchmark generations"""

    description: Optional[str] = None
    """Optional description"""

    reality_target: Optional[str] = None
    """Real‑world label"""

    simulation_engine: Optional[str] = None
    """Engine used"""

    test_finished_at: Optional[datetime] = None
    """Benchmark finished"""

    test_started_at: Optional[datetime] = None
    """Benchmark started"""

    upload_filename: Optional[str] = None
    """Original CSV filename"""


class APIResponse(BaseModel):
    data: Optional[Data] = None
    """Population model data:"""

    errors: Optional[List[Error]] = None
    """List of structured error messages, if any occurred during the request."""
