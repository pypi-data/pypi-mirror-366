import enum
from typing import Optional, List

from appodus_utils import Object
from pydantic import Field


class AccessScope(str, enum.Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    INTERNAL = "internal"

class CreateDocumentDto(Object):
    store_key: str
    access_scope: AccessScope
    store_bucket: Optional[str] = None
    tags: Optional[List[str]] = None
    owner: Optional[str] = None
    description: Optional[str] = None

class DocumentMetadata(Object):
    tags: List[str] = Field(default_factory=list)
    owner: Optional[str] = None
    description: Optional[str] = None