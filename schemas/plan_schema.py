from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Literal


class AnalysisPlan(BaseModel):
    task_type: Literal["aggregation", "breakdown", "analysis"]
    metrics: List[str]
    aggregation: Literal["sum", "mean", "count"] = "sum"
    group_by: List[str] = Field(default_factory=list)
    filters: Dict[str, Any] = Field(default_factory=dict)
    @field_validator("group_by", mode="before")
    @classmethod
    def coerce_group_by(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return v

    @field_validator("metrics", mode="before")
    @classmethod
    def coerce_metrics(cls, v):
        if isinstance(v, str):
            return [v]
        return v

    @field_validator("metrics")
    @classmethod
    def validate_metrics_not_empty(cls, v):
        if not v:
            raise ValueError("metrics must contain at least one column")
        return v
