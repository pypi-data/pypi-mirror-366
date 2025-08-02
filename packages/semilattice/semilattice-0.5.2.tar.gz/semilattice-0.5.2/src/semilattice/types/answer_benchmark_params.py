# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Required, TypeAlias, TypedDict

from .answer_param import AnswerParam

__all__ = ["AnswerBenchmarkParams", "Answers"]


class AnswerBenchmarkParams(TypedDict, total=False):
    answers: Required[Answers]
    """One or more population answers to simulate.

    A single object is accepted for convenience.
    """

    population_id: Required[str]
    """ID of the population model against which to run the simulation"""


Answers: TypeAlias = Union[AnswerParam, Iterable[AnswerParam]]
