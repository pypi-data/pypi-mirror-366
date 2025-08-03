from typing import Optional

from .URI import URI

class PlaceReference:
    identifier = 'http://gedcomx.org/v1/PlaceReference'
    version = 'http://gedcomx.org/conceptual-model/v1'
    
    def __init__(self, original: Optional[str], descriptionRef: Optional[URI]) -> None:
        self.original = original
        self.descriptionRef = descriptionRef

    @property
    def _as_dict_(self):
        return {
            'original': self.original,
            'descriptionRef': self.descriptionRef._as_dict_ if self.descriptionRef else None
            } 

def ensure_list(val):
    if val is None:
        return []
    return val if isinstance(val, list) else [val]

# PlaceReference
PlaceReference._from_json_ = classmethod(lambda cls, data: PlaceReference(
    original=data.get('original'),
    descriptionRef=URI._from_json_(data['description']) if data.get('description') else None
))

   