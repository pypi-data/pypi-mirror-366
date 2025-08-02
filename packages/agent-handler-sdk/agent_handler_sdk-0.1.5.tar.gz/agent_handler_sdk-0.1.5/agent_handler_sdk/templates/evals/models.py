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
    type: str


class ToolCallModelEvaluator(BaseEvaluator):
    type: Literal["tool_call"]
    tool_name: str
    params: dict | None


class LabelModelEvaluator(BaseEvaluator):
    type: Literal["label_model"]
    passing_labels: Optional[List[str]]
    labels: Optional[List[str]]
    model: Optional[str]
    input: List[MessageInput]


Evaluator = Union[ToolCallModelEvaluator, LabelModelEvaluator, BaseEvaluator]


class EvalMetadata(BaseModel):
    description: Optional[str]


class EvalItemInput(BaseModel, extra=Extra.allow):
    input: str


class EvalItem(BaseModel):
    id: str
    input: EvalItemInput
    tool_calls: Optional[List[Dict[str, Any]]] = None


class EvalConfig(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    data_source_config: DataSourceConfig
    testing_evaluators: List[Evaluator]
    name: str
    metadata: EvalMetadata
