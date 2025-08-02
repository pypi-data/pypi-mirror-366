# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["AnswerParam", "QuestionOptions"]


class QuestionOptions(TypedDict, total=False):
    question_type: Required[Literal["single-choice", "multiple-choice"]]
    """Type of question: one of 'single-choice' or 'multiple-choice'"""

    limit: Optional[int]
    """Maximum number of choices or responses to allow for multiple-choice questions"""


class AnswerParam(TypedDict, total=False):
    question: Required[str]
    """Text of the question"""

    question_options: Required[QuestionOptions]
    """Per-question parameters (question type, limits, etc.)"""

    answer_options: Optional[List[str]]
    """
    Possible answers presented to the simulation model (required for
    single-/multiple-choice questions).
    """

    ground_answer_counts: Optional[Dict[str, int]]
    """Ground-truth answer counts used for benchmark evaluation.

    Keyed by answer option.
    """

    ground_answer_sample_size: Optional[int]
    """Sample size of population behind ground_answer_counts.

    Reflects the numberof individuals who made selections for single and multiple
    choice questions.
    """
