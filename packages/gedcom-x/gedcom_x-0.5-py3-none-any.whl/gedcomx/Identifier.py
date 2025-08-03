
from enum import Enum

from typing import List, Optional, Dict, Any

from .Qualifier import Qualifier
from .URI import URI

class IdentifierType(Enum):
    Primary = "http://gedcomx.org/Primary"
    Authority = "http://gedcomx.org/Authority"
    Deprecated = "http://gedcomx.org/Deprecated"
    Persistant = "http://gedcomx.org/Persistent"
    
    @property
    def description(self):
        descriptions = {
            IdentifierType.Primary: (
                "The primary identifier for the resource. The value of the identifier MUST resolve to the instance of "
                "Subject to which the identifier applies."
            ),
            IdentifierType.Authority: (
                "An identifier for the resource in an external authority or other expert system. The value of the identifier "
                "MUST resolve to a public, authoritative source for information about the Subject to which the identifier applies."
            ),
            IdentifierType.Deprecated: (
                "An identifier that has been relegated, deprecated, or otherwise downgraded. This identifier is commonly used "
                "as the result of a merge when what was once a primary identifier for a resource is no longer the primary identifier. "
                "The value of the identifier MUST resolve to the instance of Subject to which the identifier applies."
            )
        }
        return descriptions.get(self, "No description available.")
    
class Identifier:
    identifier = 'http://gedcomx.org/v1/Identifier'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, value: Optional[URI], type: Optional[IdentifierType] = IdentifierType.Primary) -> None:
        self.value = value
        self.type = type
    
    
    @property
    def _as_dict_(self):
        def _serialize(value):
            if isinstance(value, (str, int, float, bool, type(None))):
                return value
            elif isinstance(value, dict):
                return {k: _serialize(v) for k, v in value.items()}
            elif isinstance(value, (list, tuple, set)):
                return [_serialize(v) for v in value]
            elif hasattr(value, "_as_dict_"):
                return value._as_dict_
            else:
                return str(value)  # fallback for unknown objects

        
        identifier_fields = {
            'value': self.value if self.value else None,
            'type': self.type.value if self.type else None
                           
        }

        # Serialize and exclude None values
        for key, value in identifier_fields.items():
            if value is not None:
                identifier_fields[key] = _serialize(value)

        return identifier_fields

    @classmethod
    def _from_json_(cls, data: Dict[str, Any]) -> 'Identifier':
        """
        Construct an Identifier from a dict parsed from JSON.
        """
        # Parse value (URI dict or string)
        
        for key in data.keys():
            type = key
            value = data[key]
        uri_obj: Optional[URI] = None
        # TODO DO THIS BETTER

        # Parse type
        raw_type = data.get('type')
        id_type: Optional[IdentifierType] = IdentifierType(raw_type)
        

        return cls(value=value, type=id_type)