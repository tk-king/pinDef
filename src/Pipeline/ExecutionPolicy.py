from enum import Enum

class ExecutionPolicy(Enum):
    OVERWRITE = "overwrite"
    CACHE = "cache"
    CACHE_ONLY = "cache_only"
