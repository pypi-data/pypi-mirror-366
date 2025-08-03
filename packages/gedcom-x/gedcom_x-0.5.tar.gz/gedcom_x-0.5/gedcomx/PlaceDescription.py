from typing import List, Optional

from .Attribution import Attribution
from .Conclusion import ConfidenceLevel
from .Date import Date
from .EvidenceReference import EvidenceReference
from .Identifier import Identifier
from .Note import Note
from .SourceReference import SourceReference
from .TextValue import TextValue
from .URI import URI

from .Subject import Subject

class PlaceDescription(Subject):
    identifier = "http://gedcomx.org/v1/PlaceDescription"
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, id: str =None,
                 lang: str = 'en',
                 sources: Optional[List[SourceReference]] = [],
                 analysis: URI = None, notes: Optional[List[Note]] =[],
                 confidence: ConfidenceLevel = None,
                 attribution: Attribution = None,
                 extracted: bool = None,
                 evidence: List[EvidenceReference] = None,
                 media: List[SourceReference] = [],
                 identifiers: List[Identifier] = [],
                 names: List[TextValue] = [],
                 type: Optional[str] = None,
                 place: Optional[URI] = None,
                 jurisdiction: Optional["PlaceDescription"] = None, # PlaceDescription
                 latitude: Optional[float] = None,
                 longitude: Optional[float] = None,
                 temporalDescription: Optional[Date] = None,
                 spatialDescription: Optional[URI] = None,) -> None:
        super().__init__(id, lang, sources, analysis, notes, confidence, attribution, extracted, evidence, media, identifiers)
        self.names = names
        self.type = type
        self.place = place
        self.jurisdiction = jurisdiction
        self.latitide = latitude
        self.longitute = longitude
        self.temporalDescription = temporalDescription
        self.spacialDescription = spatialDescription

        