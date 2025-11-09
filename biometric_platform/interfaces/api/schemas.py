"""
Pydantic schemas for API payloads.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class MatchSchema(BaseModel):
    user_id: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EnrollmentRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    samples: List[str] = Field(..., description="List of sample payloads or references")

    @field_validator("samples")
    @classmethod
    def validate_samples(cls, value: List[str]) -> List[str]:
        if not value:
            raise ValueError("samples cannot be empty")
        return value


class VerificationRequest(BaseModel):
    sample: str = Field(..., description="Single sample payload or reference")
    top_k: Optional[int] = Field(default=5, ge=1, description="Number of matches to retrieve")


class EnrollmentResponse(BaseModel):
    status: str = Field(..., description="Operation status")
    user_id: str
    stored_samples: Optional[List[str]] = Field(default=None)


class VerificationResponse(BaseModel):
    status: str
    decision: bool
    threshold: float
    matches: List[MatchSchema]


class DeleteResponse(BaseModel):
    status: str
    user_id: str


class GetResponse(BaseModel):
    status: str
    user_id: str
    modality: str
    samples: Optional[List[str]] = Field(default=None)


class ModalitiesResponse(BaseModel):
    modalities: List[str]

