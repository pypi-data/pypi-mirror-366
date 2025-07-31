from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    # REQUIRED fields expected in the body
    query: str
    model: str

    # ----- original backend fields -----
    provider_key: Optional[str] = None
    location: str = "us"
    system_prompt: Optional[str] = None
    response_language: str = "auto"
    answer_type: Literal["markdown", "html", "json"] = "markdown"
    search_type: Literal["general", "news"] = "general"
    json_schema: Optional[str] = None
    citations: bool = False
    return_sources: bool = False
    return_images: bool = False
    date_filter: Literal["hour", "day", "week","month","year","anytime"] = "anytime"
    max_tokens: int = 1500
    temperature: float = 0.7
    domain_filter: Optional[List[str]] = None
    max_queries: int = 1
    search_context_size: Literal["low", "medium", "high"] = "medium"


class SimplifiedSearchResponse(BaseModel):
    llm_response: Union[str, dict]
    response_time: float
    input_tokens: int
    output_tokens: int
    sources: list[dict] = Field(default_factory=list)
    images: list[dict] = Field(default_factory=list)
    model_cost: Optional[float] = None
    llmlayer_cost: Optional[float] = None
