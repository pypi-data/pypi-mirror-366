from typing import Optional

from .Attribution import Attribution
from .URI import URI

class EvidenceReference:
    identifier = 'http://gedcomx.org/v1/EvidenceReference'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, resource: URI, attribution: Optional[Attribution]) -> None:
        pass