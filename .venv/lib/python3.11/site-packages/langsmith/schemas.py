"""Schemas for the LangSmith API."""
from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Protocol,
    Union,
    runtime_checkable,
)
from uuid import UUID

from typing_extensions import TypedDict

try:
    from pydantic.v1 import (  # type: ignore[import]
        BaseModel,
        Field,
        PrivateAttr,
        StrictBool,
        StrictFloat,
        StrictInt,
    )
except ImportError:
    from pydantic import (  # type: ignore[assignment]
        BaseModel,
        Field,
        PrivateAttr,
        StrictBool,
        StrictFloat,
        StrictInt,
    )

from typing_extensions import Literal

SCORE_TYPE = Union[StrictBool, StrictInt, StrictFloat, None]
VALUE_TYPE = Union[Dict, StrictBool, StrictInt, StrictFloat, str, None]


class ExampleBase(BaseModel):
    """Example base model."""

    dataset_id: UUID
    inputs: Dict[str, Any]
    outputs: Optional[Dict[str, Any]] = Field(default=None)

    class Config:
        frozen = True


class ExampleCreate(ExampleBase):
    """Example create model."""

    id: Optional[UUID]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Example(ExampleBase):
    """Example model."""

    id: UUID
    created_at: datetime
    modified_at: Optional[datetime] = Field(default=None)
    runs: List[Run] = Field(default_factory=list)
    source_run_id: Optional[UUID] = None
    _host_url: Optional[str] = PrivateAttr(default=None)
    _tenant_id: Optional[UUID] = PrivateAttr(default=None)

    def __init__(
        self,
        _host_url: Optional[str] = None,
        _tenant_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a Dataset object."""
        super().__init__(**kwargs)
        self._host_url = _host_url
        self._tenant_id = _tenant_id

    @property
    def url(self) -> Optional[str]:
        """URL of this run within the app."""
        if self._host_url:
            path = f"/datasets/{self.dataset_id}/e/{self.id}"
            if self._tenant_id:
                return f"{self._host_url}/o/{str(self._tenant_id)}{path}"
            return f"{self._host_url}{path}"
        return None


class ExampleUpdate(BaseModel):
    """Update class for Example."""

    dataset_id: Optional[UUID] = None
    inputs: Optional[Dict[str, Any]] = None
    outputs: Optional[Dict[str, Any]] = None

    class Config:
        frozen = True


class DataType(str, Enum):
    """Enum for dataset data types."""

    kv = "kv"
    llm = "llm"
    chat = "chat"


class DatasetBase(BaseModel):
    """Dataset base model."""

    name: str
    description: Optional[str] = None
    data_type: Optional[DataType] = None

    class Config:
        frozen = True


class DatasetCreate(DatasetBase):
    """Dataset create model."""

    id: Optional[UUID] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Dataset(DatasetBase):
    """Dataset ORM model."""

    id: UUID
    created_at: datetime
    modified_at: Optional[datetime] = Field(default=None)
    example_count: Optional[int] = None
    session_count: Optional[int] = None
    last_session_start_time: Optional[datetime] = None
    _host_url: Optional[str] = PrivateAttr(default=None)
    _tenant_id: Optional[UUID] = PrivateAttr(default=None)
    _public_path: Optional[str] = PrivateAttr(default=None)

    def __init__(
        self,
        _host_url: Optional[str] = None,
        _tenant_id: Optional[UUID] = None,
        _public_path: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a Dataset object."""
        super().__init__(**kwargs)
        self._host_url = _host_url
        self._tenant_id = _tenant_id
        self._public_path = _public_path

    @property
    def url(self) -> Optional[str]:
        """URL of this run within the app."""
        if self._host_url:
            if self._public_path:
                return f"{self._host_url}{self._public_path}"
            if self._tenant_id:
                return f"{self._host_url}/o/{str(self._tenant_id)}/datasets/{self.id}"
            return f"{self._host_url}/datasets/{self.id}"
        return None


class RunTypeEnum(str, Enum):
    """(Deprecated) Enum for run types. Use string directly."""

    tool = "tool"
    chain = "chain"
    llm = "llm"
    retriever = "retriever"
    embedding = "embedding"
    prompt = "prompt"
    parser = "parser"


class RunBase(BaseModel):
    """
    Base Run schema.
    Contains the fundamental fields to define a run in a system.
    """

    id: UUID
    """Unique identifier for the run."""

    name: str
    """Human-readable name for the run."""

    start_time: datetime
    """Start time of the run."""

    run_type: str
    """The type of run, such as tool, chain, llm, retriever,
    embedding, prompt, parser."""

    end_time: Optional[datetime] = None
    """End time of the run, if applicable."""

    extra: Optional[dict] = None
    """Additional metadata or settings related to the run."""

    error: Optional[str] = None
    """Error message, if the run encountered any issues."""

    serialized: Optional[dict] = None
    """Serialized object that executed the run for potential reuse."""

    events: Optional[List[Dict]] = None
    """List of events associated with the run, like
    start and end events."""

    inputs: dict
    """Inputs used for the run."""

    outputs: Optional[dict] = None
    """Outputs generated by the run, if any."""

    reference_example_id: Optional[UUID] = None
    """Reference to an example that this run may be based on."""

    parent_run_id: Optional[UUID] = None
    """Identifier for a parent run, if this run is a sub-run."""

    tags: Optional[List[str]] = None
    """Tags for categorizing or annotating the run."""


class Run(RunBase):
    """Run schema when loading from the DB."""

    session_id: Optional[UUID] = None
    """The project ID this run belongs to."""
    child_run_ids: Optional[List[UUID]] = None
    """The child run IDs of this run."""
    child_runs: Optional[List[Run]] = None
    """The child runs of this run, if instructed to load using the client
    These are not populated by default, as it is a heavier query to make."""
    feedback_stats: Optional[Dict[str, Any]] = None
    """Feedback stats for this run."""
    app_path: Optional[str] = None
    """Relative URL path of this run within the app."""
    manifest_id: Optional[UUID] = None
    """Unique ID of the serialized object for this run."""
    status: Optional[str] = None
    """Status of the run (e.g., 'success')."""
    prompt_tokens: Optional[int] = None
    """Number of tokens used for the prompt."""
    completion_tokens: Optional[int] = None
    """Number of tokens generated as output."""
    total_tokens: Optional[int] = None
    """Total tokens for prompt and completion."""
    first_token_time: Optional[datetime] = None
    """Time the first token was processed."""
    parent_run_ids: Optional[List[UUID]] = None
    """List of parent run IDs."""
    trace_id: UUID
    """Unique ID assigned to every run within this nested trace."""
    dotted_order: str = Field(default="")
    """Dotted order for the run.

    This is a string composed of {time}{run-uuid}.* so that a trace can be
    sorted in the order it was executed.

    Example:
    - Parent: 20230914T223155647Z1b64098b-4ab7-43f6-afee-992304f198d8
    - Children:
        - 20230914T223155647Z1b64098b-4ab7-43f6-afee-992304f198d8.20230914T223155649Z809ed3a2-0172-4f4d-8a02-a64e9b7a0f8a
        - 20230915T223155647Z1b64098b-4ab7-43f6-afee-992304f198d8.20230914T223155650Zc8d9f4c5-6c5a-4b2d-9b1c-3d9d7a7c5c7c
    """  # noqa: E501
    _host_url: Optional[str] = PrivateAttr(default=None)

    def __init__(self, _host_url: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize a Run object."""
        if not kwargs.get("trace_id"):
            kwargs = {"trace_id": kwargs.get("id"), **kwargs}
        super().__init__(**kwargs)
        self._host_url = _host_url
        if not self.dotted_order.strip() and not self.parent_run_id:
            self.dotted_order = f"{self.start_time.isoformat()}{self.id}"

    @property
    def url(self) -> Optional[str]:
        """URL of this run within the app."""
        if self._host_url and self.app_path:
            return f"{self._host_url}{self.app_path}"
        return None


class RunLikeDict(TypedDict, total=False):
    """Run-like dictionary, for type-hinting."""

    name: str
    run_type: RunTypeEnum
    start_time: datetime
    inputs: Optional[dict]
    outputs: Optional[dict]
    end_time: Optional[datetime]
    extra: Optional[dict]
    error: Optional[str]
    serialized: Optional[dict]
    parent_run_id: Optional[UUID]
    manifest_id: Optional[UUID]
    events: Optional[List[dict]]
    tags: Optional[List[str]]
    inputs_s3_urls: Optional[dict]
    outputs_s3_urls: Optional[dict]
    id: Optional[UUID]
    session_id: Optional[UUID]
    session_name: Optional[str]
    reference_example_id: Optional[UUID]
    input_attachments: Optional[dict]
    output_attachments: Optional[dict]
    trace_id: UUID
    dotted_order: str


class RunWithAnnotationQueueInfo(RunBase):
    """Run schema with annotation queue info."""

    last_reviewed_time: Optional[datetime] = None
    """The last time this run was reviewed."""
    added_at: Optional[datetime] = None
    """The time this run was added to the queue."""


class FeedbackSourceBase(BaseModel):
    type: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class APIFeedbackSource(FeedbackSourceBase):
    """API feedback source."""

    type: Literal["api"] = "api"


class ModelFeedbackSource(FeedbackSourceBase):
    """Model feedback source."""

    type: Literal["model"] = "model"


class FeedbackSourceType(Enum):
    """Feedback source type."""

    API = "api"
    """General feedback submitted from the API."""
    MODEL = "model"
    """Model-assisted feedback."""


class FeedbackBase(BaseModel):
    """Feedback schema."""

    id: UUID
    """The unique ID of the feedback."""
    created_at: Optional[datetime] = None
    """The time the feedback was created."""
    modified_at: Optional[datetime] = None
    """The time the feedback was last modified."""
    run_id: UUID
    """The associated run ID this feedback is logged for."""
    key: str
    """The metric name, tag, or aspect to provide feedback on."""
    score: SCORE_TYPE = None
    """Value or score to assign the run."""
    value: VALUE_TYPE = None
    """The display value, tag or other value for the feedback if not a metric."""
    comment: Optional[str] = None
    """Comment or explanation for the feedback."""
    correction: Union[str, dict, None] = None
    """Correction for the run."""
    feedback_source: Optional[FeedbackSourceBase] = None
    """The source of the feedback."""

    class Config:
        frozen = True


class FeedbackCreate(FeedbackBase):
    """Schema used for creating feedback."""

    feedback_source: FeedbackSourceBase
    """The source of the feedback."""


class Feedback(FeedbackBase):
    """Schema for getting feedback."""

    id: UUID
    created_at: datetime
    """The time the feedback was created."""
    modified_at: datetime
    """The time the feedback was last modified."""
    feedback_source: Optional[FeedbackSourceBase] = None
    """The source of the feedback. In this case"""


class TracerSession(BaseModel):
    """TracerSession schema for the API.

    Sessions are also referred to as "Projects" in the UI.
    """

    id: UUID
    """The ID of the project."""
    start_time: datetime = Field(default_factory=datetime.utcnow)
    """The time the project was created."""
    end_time: Optional[datetime] = None
    """The time the project was ended."""
    description: Optional[str] = None
    """The description of the project."""
    name: Optional[str] = None
    """The name of the session."""
    extra: Optional[Dict[str, Any]] = None
    """Extra metadata for the project."""
    tenant_id: UUID
    """The tenant ID this project belongs to."""

    _host_url: Optional[str] = PrivateAttr(default=None)

    def __init__(self, _host_url: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize a Run object."""
        super().__init__(**kwargs)
        self._host_url = _host_url

    @property
    def url(self) -> Optional[str]:
        """URL of this run within the app."""
        if self._host_url:
            return f"{self._host_url}/o/{self.tenant_id}/projects/p/{self.id}"
        return None

    @property
    def metadata(self) -> dict[str, Any]:
        """Retrieve the metadata (if any)."""
        if self.extra is None or "metadata" not in self.extra:
            return {}
        return self.extra["metadata"]

    @property
    def tags(self) -> List[str]:
        """Retrieve the tags (if any)."""
        if self.extra is None or "tags" not in self.extra:
            return []
        return self.extra["tags"]


class TracerSessionResult(TracerSession):
    """TracerSession schema returned when reading a project
    by ID. Sessions are also referred to as "Projects" in the UI."""

    run_count: Optional[int]
    """The number of runs in the project."""
    latency_p50: Optional[timedelta]
    """The median (50th percentile) latency for the project."""
    latency_p99: Optional[timedelta]
    """The 99th percentile latency for the project."""
    total_tokens: Optional[int]
    """The total number of tokens consumed in the project."""
    prompt_tokens: Optional[int]
    """The total number of prompt tokens consumed in the project."""
    completion_tokens: Optional[int]
    """The total number of completion tokens consumed in the project."""
    last_run_start_time: Optional[datetime]
    """The start time of the last run in the project."""
    feedback_stats: Optional[Dict[str, Any]]
    """Feedback stats for the project."""
    reference_dataset_ids: Optional[List[UUID]]
    """The reference dataset IDs this project's runs were generated on."""
    run_facets: Optional[List[Dict[str, Any]]]
    """Facets for the runs in the project."""


@runtime_checkable
class BaseMessageLike(Protocol):
    """
    A protocol representing objects similar to BaseMessage.
    """

    content: str
    additional_kwargs: Dict

    @property
    def type(self) -> str:
        """Type of the Message, used for serialization."""


class DatasetShareSchema(TypedDict, total=False):
    dataset_id: UUID
    share_token: UUID
    url: str


class AnnotationQueue(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tenant_id: UUID


class BatchIngestConfig(TypedDict, total=False):
    scale_up_qsize_trigger: int
    scale_up_nthreads_limit: int
    scale_down_nempty_trigger: int
    size_limit: int


class LangSmithInfo(BaseModel):
    """Information about the LangSmith server."""

    version: str = ""
    """The version of the LangSmith server."""
    license_expiration_time: Optional[datetime] = None
    """The time the license will expire."""
    batch_ingest_config: Optional[BatchIngestConfig] = None


Example.update_forward_refs()
