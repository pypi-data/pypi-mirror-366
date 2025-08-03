import base64
import uuid
import warnings

from typing import List, Optional

from .Attribution import Attribution
from .Note import Note
from .Qualifier import Qualifier
from .SourceReference import SourceReference
from .URI import URI

class ConfidenceLevel(Qualifier):
    High = "http://gedcomx.org/High"
    Medium = "http://gedcomx.org/Medium"
    Low = "http://gedcomx.org/Low"
    
    @property
    def description(self):
        descriptions = {
            ConfidenceLevel.High: "The contributor has a high degree of confidence that the assertion is true.",
            ConfidenceLevel.Medium: "The contributor has a medium degree of confidence that the assertion is true.",
            ConfidenceLevel.Low: "The contributor has a low degree of confidence that the assertion is true."
        }
        return descriptions.get(self, "No description available.")
    
class Conclusion:
    identifier = 'http://gedcomx.org/v1/Conclusion'
    version = 'http://gedcomx.org/conceptual-model/v1'

    @staticmethod
    def default_id_generator():
        # Generate a standard UUID
        standard_uuid = uuid.uuid4()
        # Convert UUID to bytes
        uuid_bytes = standard_uuid.bytes
        # Encode bytes to a Base64 string
        short_uuid = base64.urlsafe_b64encode(uuid_bytes).rstrip(b'=').decode('utf-8')
        return short_uuid
    
    def __init__(self,
                 id: Optional[str],
                 lang: Optional[str] = 'en',
                 sources: Optional[List[SourceReference]] = [],
                 analysis: Optional[URI] = None,
                 notes: Optional[List[Note]] = [],
                 confidence: Optional[ConfidenceLevel] = None,
                 attribution: Optional[Attribution] = None,
                 uri: Optional[URI] = None,
                 max_note_count: int = 20) -> None:
        
        self._id_generator = Conclusion.default_id_generator

        self.id = id if id else self._id_generator()
        self.lang = lang
        self.sources = sources
        self.analysis = analysis
        self.notes = notes
        self.confidence = confidence
        self.attribution = attribution
        self.max_note_count = max_note_count
        self._uri = uri if uri else URI(fragment=id)
    
    def add_note(self,note_to_add: Note):
        if len(self.notes) >= self.max_note_count:
            warnings.warn(f"Max not count of {self.max_note_count} reached for id: {self.id}")
            return False
        if note_to_add and isinstance(note_to_add,Note):
            for existing in self.notes:
                if note_to_add == existing:
                    return False
            self.notes.append(note_to_add)

    def add_source(self, source_to_add: SourceReference):
        if source_to_add and isinstance(source_to_add,SourceReference):
            for current_source in self.sources:
                if source_to_add == current_source:
                    return
            self.sources.append(source_to_add)
        else:
            raise ValueError()
    
    '''
    def _as_dict_(self):
        return {
            'id':self.id,
            'lang':self.lang,
            'sources': [source._prop_dict() for source in self.sources] if self.sources else None,
            'analysis': self.analysis._uri if self.analysis else None,
            'notes':"Add notes here",
            'confidence':self.confidence
        }
    '''
    
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

        # Only add Relationship-specific fields
        conclusion_fields = {
            'id':self.id,
            'lang':self.lang,
            'sources': [source for source in self.sources] if self.sources else None,
            'analysis': self.analysis._uri if self.analysis else None,
            'notes': [note for note in self.notes] if self.notes else None,
            'confidence':self.confidence
        }

        # Serialize and exclude None values
        for key, value in conclusion_fields.items():
            if value is not None:
                                conclusion_fields[key] = _serialize(value)
        return conclusion_fields
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        
        return (
            self.id == other.id and
            self.lang == other.lang and
            self.sources == other.sources and
            self.analysis == other.analysis and
            self.notes == other.notes and
            self.confidence == other.confidence and
            self.attribution == other.attribution
        )