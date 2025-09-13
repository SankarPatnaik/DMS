from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class Document(BaseModel):
    id: str
    title: str
    storage_key: str
    size_bytes: int
    checksum: str
    mime_type: str
    classification: str = "internal"
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, str] = Field(default_factory=dict)
    created_by: str
    created_at: datetime
    updated_at: datetime
    current_version_id: Optional[str] = None


class DocumentVersion(BaseModel):
    id: str
    document_id: str
    version_no: int
    storage_key: str
    checksum: str
    created_by: str
    created_at: datetime
    change_note: Optional[str] = None
