from typing import Literal, Optional

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    budget: int = Field(gt=0, le=100_000_000)
    purpose: Literal["game", "dev", "ai", "creative", "office", "daily"]
    resolution: Literal["1080p", "1440p", "4K"] = "1080p"
    cpu_preference: Literal["Intel", "AMD", "any"] = "any"
    gpu_preference: Literal["NVIDIA", "AMD", "any"] = "any"
    memory: Literal[16, 32, 64] = 32
    storage: Literal[500, 1000, 2000] = 1000
    include: list[Literal["monitor", "keyboard"]] = Field(default_factory=list)
    game: Optional[str] = None
    notes: Optional[str] = None
