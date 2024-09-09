import asyncio
import uuid
from abc import abstractmethod
from typing import Callable, Dict, List, Optional, TypedDict, Union, cast

try:
    from pydantic.v1 import BaseModel, Field, ValidationError  # type: ignore[import]
except ImportError:
    from pydantic import BaseModel, Field, ValidationError

from functools import wraps

from langsmith.schemas import SCORE_TYPE, VALUE_TYPE, Example, Run


class EvaluationResult(BaseModel):
    """Evaluation result."""

    key: str
    """The aspect, metric name, or label for this evaluation."""
    score: SCORE_TYPE = None
    """The numeric score for this evaluation."""
    value: VALUE_TYPE = None
    """The value for this evaluation, if not numeric."""
    comment: Optional[str] = None
    """An explanation regarding the evaluation."""
    correction: Optional[Dict] = None
    """What the correct value should be, if applicable."""
    evaluator_info: Dict = Field(default_factory=dict)
    """Additional information about the evaluator."""
    source_run_id: Optional[Union[uuid.UUID, str]] = None
    """The ID of the trace of the evaluator itself."""
    target_run_id: Optional[Union[uuid.UUID, str]] = None
    """The ID of the trace this evaluation is applied to.
    
    If none provided, the evaluation feedback is applied to the
    root trace being."""

    class Config:
        """Pydantic model configuration."""

        allow_extra = False


class EvaluationResults(TypedDict, total=False):
    """Batch evaluation results, if your evaluator wishes
    to return multiple scores."""

    results: List[EvaluationResult]
    """The evaluation results."""


class RunEvaluator:
    """Evaluator interface class."""

    @abstractmethod
    def evaluate_run(
        self, run: Run, example: Optional[Example] = None
    ) -> Union[EvaluationResult, EvaluationResults]:
        """Evaluate an example."""

    async def aevaluate_run(
        self, run: Run, example: Optional[Example] = None
    ) -> Union[EvaluationResult, EvaluationResults]:
        """Evaluate an example asynchronously."""
        return await asyncio.get_running_loop().run_in_executor(
            None, self.evaluate_run, run, example
        )


class DynamicRunEvaluator(RunEvaluator):
    """
    A dynamic evaluator that wraps a function and transforms it into a `RunEvaluator`.

    This class is designed to be used with the `@run_evaluator` decorator, allowing
    functions that take a `Run` and an optional `Example` as arguments, and return
    an `EvaluationResult` or `EvaluationResults`, to be used as instances of `RunEvaluator`.

    Attributes:
        func (Callable): The function that is wrapped by this evaluator.
    """  # noqa: E501

    def __init__(
        self,
        func: Callable[
            [Run, Optional[Example]], Union[EvaluationResult, EvaluationResults, dict]
        ],
    ):
        """
        Initialize the DynamicRunEvaluator with a given function.

        Args:
            func (Callable): A function that takes a `Run` and an optional `Example` as
            arguments, and returns an `EvaluationResult` or `EvaluationResults`.
        """
        wraps(func)(self)
        self.func = func

    def _coerce_evaluation_result(
        self,
        result: Union[EvaluationResult, dict],
        allow_no_key: bool = False,
    ) -> EvaluationResult:
        if isinstance(result, EvaluationResult):
            return result
        try:
            if "key" not in result:
                if allow_no_key:
                    result["key"] = self.func.__name__
            return EvaluationResult(**result)
        except ValidationError as e:
            raise ValueError(
                "Expected an EvaluationResult object, or dict with a metric"
                f" 'key' and optional 'score'; got {result}"
            ) from e

    def _coerce_evaluation_results(
        self,
        results: Union[dict, EvaluationResults],
    ) -> Union[EvaluationResult, EvaluationResults]:
        if "results" in results:
            cp = results.copy()
            cp["results"] = [
                self._coerce_evaluation_result(r) for r in results["results"]
            ]
            return EvaluationResults(**cp)

        return self._coerce_evaluation_result(cast(dict, results), allow_no_key=True)

    def evaluate_run(
        self, run: Run, example: Optional[Example] = None
    ) -> Union[EvaluationResult, EvaluationResults]:
        """
        Evaluate a run using the wrapped function.

        This method directly invokes the wrapped function with the provided arguments.

        Args:
            run (Run): The run to be evaluated.
            example (Optional[Example]): An optional example to be used in the evaluation.

        Returns:
            Union[EvaluationResult, EvaluationResults]: The result of the evaluation.
        """  # noqa: E501
        result = self.func(run, example)
        if isinstance(result, EvaluationResult):
            return result
        if not isinstance(result, dict):
            raise ValueError(
                f"Expected a dict, EvaluationResult, or EvaluationResults, got {result}"
            )
        return self._coerce_evaluation_results(result)

    def __call__(
        self, run: Run, example: Optional[Example] = None
    ) -> Union[EvaluationResult, EvaluationResults]:
        """
        Make the evaluator callable, allowing it to be used like a function.

        This method enables the evaluator instance to be called directly, forwarding the
        call to `evaluate_run`.

        Args:
            run (Run): The run to be evaluated.
            example (Optional[Example]): An optional example to be used in the evaluation.

        Returns:
            Union[EvaluationResult, EvaluationResults]: The result of the evaluation.
        """  # noqa: E501
        return self.evaluate_run(run, example)


def run_evaluator(
    func: Callable[
        [Run, Optional[Example]], Union[EvaluationResult, EvaluationResults, dict]
    ],
):
    """Decorator to create a run evaluator from a function."""
    return DynamicRunEvaluator(func)
