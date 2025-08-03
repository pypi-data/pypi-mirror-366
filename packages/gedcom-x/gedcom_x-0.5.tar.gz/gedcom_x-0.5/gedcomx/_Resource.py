from typing import Any
from .URI import URI

class Resource:
    def __init__(self, obj: Any):
        if isinstance(obj,URI):
            pass
        elif hasattr(obj,'_uri'):
            pass
        else:
            return None