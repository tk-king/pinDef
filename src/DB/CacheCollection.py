from typing import Any, Optional
from beanie import Document, PydanticObjectId

class CacheCollection(Document):
    step_key: str
    input_key: PydanticObjectId
    value: Optional[Any] = None
    exception: Optional[str] = None
