# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

from .._types import FileTypes

__all__ = ["PopulationCreateParams", "PopulationOptions", "PopulationOptionsQuestionOption"]


class PopulationCreateParams(TypedDict, total=False):
    name: Required[str]

    population_options: Required[PopulationOptions]
    """**Important:** the API expects population_options to be sent as JSON string.

    Use json.dumps() to convert your object to string format for multipart/form-data
    requests.
    """

    seed_data: Required[FileTypes]

    simulation_engine: Required[str]

    description: Optional[str]

    reality_target: Optional[str]

    run_test: Optional[bool]


class PopulationOptionsQuestionOption(TypedDict, total=False):
    question_number: Required[int]
    """
    The column index number of the question to which the options apply (1-based),
    ignoring the first `sim_id` column
    """

    question_type: Required[Literal["single-choice", "multiple-choice", "open-ended"]]
    """Type of question: one of 'single-choice', 'multiple-choice', or 'open-ended'"""

    limit: Optional[int]
    """
    Maximum number of choices or responses which were allowed for multiple-choice
    questions
    """


class PopulationOptions(TypedDict, total=False):
    question_options: Required[Iterable[PopulationOptionsQuestionOption]]
    """
    Tells API if the columns in the seed data are single-choice, multiple-choice, or
    open-ended.If multiple choice, specifies if it was limited choice (eg. 'up to
    3').This makes sure that test simulations are run correctly when test population
    is run.
    """
