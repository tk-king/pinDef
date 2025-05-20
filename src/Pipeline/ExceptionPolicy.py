from enum import Enum

class ExceptionPolicy(Enum):
    TRY = "try"         # Attempt to fix or retry execution on error, and save the exception
    THROW = "throw"     # Raise the exception and do not save
    IGNORE = "ignore"   # Ignore the exception and return None, do not save