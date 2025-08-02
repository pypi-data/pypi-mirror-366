from typing import List, Dict, Any, Optional, Literal, Union
from pydantic import BaseModel, Extra
from datetime import datetime


class JsonSchema(BaseModel):
    type: Optional[str] = None
    properties: Optional[Dict[str, "JsonSchema"]] = None
    items: Optional[Union["JsonSchema", List["JsonSchema"]]] = None
    required: Optional[List[str]] = None
    enum: Optional[List[Any]] = None
    description: Optional[str] = None
    additional_properties: Optional[Union[bool, "JsonSchema"]] = None
    model: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"


JsonSchema.model_rebuild()


class DataSourceConfig(BaseModel):
    input_schema: JsonSchema


class MessageContent(BaseModel):
    type: str
    text: str


class MessageInput(BaseModel):
    type: str
    role: str
    content: MessageContent


class BaseEvaluator(BaseModel):
    name: str
    id: str
    type: str  # Discriminator for future extension


class ReferenceToolCallsMatchEvaluator(BaseEvaluator):
    type: Literal["reference_tool_calls_match"]
    enforce_ordering: bool
    fail_on_args_mismatch: bool


class LabelModelEvaluator(BaseEvaluator):
    type: Literal["label_model"]
    passing_labels: Optional[List[str]]
    labels: Optional[List[str]]
    model: Optional[str]
    input: List[MessageInput]


Evaluator = Union[ReferenceToolCallsMatchEvaluator, LabelModelEvaluator, BaseEvaluator]


class EvalMetadata(BaseModel):
    description: Optional[str]


class EvalItemInput(BaseModel, extra=Extra.allow):
    input: str


class EvalItem(BaseModel, extra=Extra.allow):
    """
    Schema for individual eval items.
    Supports both runtime evaluation (with id and tool_calls) and connector eval files (flexible input).
    """

    input: Union[str, EvalItemInput]  # Can be either a string or EvalItemInput object
    id: Optional[str] = None  # Optional for connector eval files


class ConnectorEvalBundle(BaseModel):
    """
    Schema for eval bundles stored in connector /evals/ folders.
    This matches the JSON structure that contains config, items, and prompts together.
    """

    data_source_config: DataSourceConfig
    items: List[EvalItem]
    prompts: List[MessageInput]
    name: str
    metadata: Optional[EvalMetadata] = None

    def to_eval_config(self) -> "EvalConfig":
        """
        Convert this bundle to an EvalConfig for use with the eval runner.
        Note: This creates a minimal EvalConfig without testing_evaluators.
        """
        return EvalConfig(
            id=None,
            created_at=None,
            updated_at=None,
            data_source_config=self.data_source_config,
            testing_evaluators=[],  # Empty list since connector evals don't define evaluators
            metadata=self.metadata,
        )


class EvalConfig(BaseModel):
    id: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    data_source_config: DataSourceConfig
    testing_evaluators: Optional[List[Evaluator]] = []
    metadata: Optional[EvalMetadata]
