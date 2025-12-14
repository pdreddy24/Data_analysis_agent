from __future__ import annotations

from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field


TaskType = Literal["aggregation", "summary", "data_quality", "visualization"]


class AnalysisPlan(BaseModel):
    task_type: TaskType

    # core intent params
    metrics: List[str] = Field(default_factory=list)
    group_by: List[str] = Field(default_factory=list)
    filters: Dict[str, Any] = Field(default_factory=dict)

    # aggregation params
    agg: str = "sum"               # sum/mean/min/max/count/std
    top_k: Optional[int] = None
    sort_desc: bool = True

    # viz params
    chart_type: Optional[str] = None   # bar/line/hist/scatter
    x: Optional[str] = None
    y: Optional[str] = None
