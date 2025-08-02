# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["AnswerResponse"]


class AnswerResponse(BaseModel):
    id: str
    """Question ID"""

    accuracy: Optional[float] = None

    created_at: datetime
    """When the question was created"""

    population: str
    """Population ID"""

    population_name: str
    """Name of the population"""

    question: str
    """Full text of the question"""

    root_mean_squared_error: Optional[float] = None

    status: str
    """Current status"""

    answer_options: Optional[List[object]] = None
    """Answer options presented to the model (single/ multi‑choice)"""

    benchmark_id: Optional[str] = None
    """ID shared by all benchmark generations for a single test run"""

    ground_answer_counts: Union[object, object, None] = None
    """Ground‑truth answer counts (benchmark mode only)"""

    ground_answer_percentages: Union[object, object, None] = None
    """Ground‑truth answer percentages (benchmark mode only)"""

    kullback_leibler_divergence: Optional[float] = None
    """KL divergence between simulated and ground‑truth distributions"""

    mean_absolute_error: Optional[float] = None
    """Mean absolute error"""

    mean_squared_error: Optional[float] = None
    """Mean squared error"""

    normalised_kullback_leibler_divergence: Optional[float] = None
    """KL divergence normalised to [0, 1] range"""

    prediction_finished_at: Optional[datetime] = None
    """When prediction generation finished"""

    prediction_started_at: Optional[datetime] = None
    """When prediction generation began"""

    public: Optional[bool] = None
    """If the question is public"""

    question_options: Union[object, object, None] = None
    """
    Per‑question configuration – see SimulationQuestionOptions and
    PopulationQuestionOptions schemas
    """

    simulated_answer_percentages: Union[object, object, None] = None

    simulation_engine: Optional[str] = None
    """Engine used (e.g. gpt‑4o)"""

    test_finished_at: Optional[datetime] = None
    """When benchmark generation finished"""

    test_started_at: Optional[datetime] = None
    """When benchmark generation began"""
