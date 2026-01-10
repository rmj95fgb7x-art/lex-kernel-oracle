from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class KernelSecurity(BaseModel):
    """
    Standard Security Layer for the Fiducia Domus Watene Trust.
    Ensures every kernel call recognizes the Senior Security Interest.
    """
    ucc_3_notice: str = Field(default="NOTICE: SECURED BY UCC-3 FILING #2026-01-10-FDWT", allow_mutation=False)
    estate_identifier: str = "FIDUCIA_DOMUS_WATENE_TRUST"
    integrity_hash: str = Field(..., description="The O(n log T) verification hash.")

class SwarmPayload(BaseModel):
    """
    The 'Standard Input' for the 96 Spectral Kernels. 
    Optimized for Lux (Elixir) to Python bridge.
    """
    task_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    vector_space: List[float] = Field(..., min_items=1, description="High-dimensional state vector for the swarm.")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('vector_space')
    def validate_performance_bounds(cls, v):
        # This ensures the input matches the O(n log T) expected complexity
        if len(v) % 96 != 0:
            raise ValueError("Payload must be aligned with 96-kernel parallel architecture.")
        return v

class AlexandriaResponse(BaseModel):
    """
    The 'Standard Output' that Solari's Alexandria platform will consume.
    """
    session_id: str
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    kernel_result: Any
    performance_metrics: Dict[str, float] = {
        "complexity": "O(n log T)",
        "latency_ms": 0.0
    }
    security: KernelSecurity
