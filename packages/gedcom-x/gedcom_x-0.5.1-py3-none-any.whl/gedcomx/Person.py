from enum import Enum
from typing import List, Optional

from .Attribution import Attribution
from .Conclusion import ConfidenceLevel
from .EvidenceReference import EvidenceReference
from .Fact import Fact
from .Gender import Gender, GenderType
from .Identifier import Identifier
from .Name import Name, NameForm, NamePart, NamePartType, NamePartQualifier
from .Note import Note
from .SourceReference import SourceReference
from .Subject import Subject
from .URI import URI

class Person(Subject):
    identifier = 'http://gedcomx.org/v1/Person'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, id: str = None,
             lang: str = 'en',
             sources: Optional[List[SourceReference]] = None,
             analysis: Optional[URI] = None,
             notes: Optional[List[Note]] = None,
             confidence: Optional[ConfidenceLevel] = None,
             attribution: Optional[Attribution] = None,
             extracted: bool = None,
             evidence: Optional[List[EvidenceReference]] = None,
             media: Optional[List[SourceReference]] = None,
             identifiers: Optional[List[Identifier]] = None,
             private: Optional[bool] = False,
             gender: Optional[Gender] = Gender(type=GenderType.Unknown),
             names: Optional[List[Name]] = None,
             facts: Optional[List[Fact]] = None,
             living: Optional[bool] = False) -> None:
        # Call superclass initializer if needed
        super().__init__(id, lang, sources, analysis, notes, confidence, attribution, extracted, evidence, media, identifiers)
        
        # Initialize mutable attributes to empty lists if None
        self.sources = sources if sources is not None else []
        self.notes = notes if notes is not None else []
        self.evidence = evidence if evidence is not None else []
        self.media = media if media is not None else []
        self.identifiers = identifiers if identifiers is not None else []
        self.names = names if names is not None else []
        self.facts = facts if facts is not None else []

        self.private = private
        self.gender = gender

        self.living = living       #TODO This is from familysearch API

        self._relationships = []
        
    
    def add_fact(self, fact_to_add: Fact) -> bool:
        if fact_to_add and isinstance(fact_to_add,Fact):
            for current_fact in self.facts:
                if fact_to_add == current_fact:
                    return False
            self.facts.append(fact_to_add)
            return True

    def add_name(self, name_to_add: Name) -> bool:
        if len(self.names) > 5: 
            for name in self.names:
                print(name)
            raise
        if name_to_add and isinstance(name_to_add, Name):
            for current_name in self.names:
                if name_to_add == current_name:
                    return False
            self.names.append(name_to_add)
            return True
    
    def _add_relationship(self, relationship_to_add: object):
        from .Relationship import Relationship
        if isinstance(relationship_to_add,Relationship):
            self._relationships.append(relationship_to_add)
        else:
            raise ValueError()
    
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

        subject_fields = super()._as_dict_  # Start with base class fields
        # Only add Relationship-specific fields
        subject_fields.update({
            'private': self.private,
            'living': self.living,
            'gender': self.gender.type.value if self.gender.type else None,
            'names': [name for name in self.names],
            'facts': [fact for fact in self.facts]
                           
        })

        # Serialize and exclude None values
        for key, value in subject_fields.items():
            if value is not None:
                subject_fields[key] = _serialize(value)

        return subject_fields
    
    
    @classmethod
    def _from_json_(cls, data: dict):
        """
        Create a Person instance from a JSON-dict (already parsed).
        """
        def ensure_list(value):
            if value is None:
                return []
            if isinstance(value, list):
                return value
            return [value]  # wrap single item in list
        
        # Basic scalar fields
        id_        = data.get('id')
        lang       = data.get('lang', 'en')
        private    = data.get('private', False)
        extracted  = data.get('extracted', False)

        living  = data.get('extracted', False)

        # Complex singletons
        analysis    = URI._from_json_(data['analysis']) if data.get('analysis') else None
        attribution = Attribution._from_json_(data['attribution']) if data.get('attribution') else None
        confidence  = ConfidenceLevel._from_json_(data['confidence']) if data.get('confidence') else None

        # Gender (string or dict depending on your JSON)
        gender_json = data.get('gender')
        if isinstance(gender_json, dict):
            gender = Gender._from_json_(gender_json)
        else:
            # if it's just the enum value
            gender = Gender(type=GenderType(gender_json)) if gender_json else Gender(type=GenderType.Unknown)
        
        
        sources     = [SourceReference._from_json_(o)   for o in ensure_list(data.get('sources'))]
        notes       = [Note._from_json_(o)              for o in ensure_list(data.get('notes'))]
        evidence    = [EvidenceReference._from_json_(o) for o in ensure_list(data.get('evidence'))]
        media       = [SourceReference._from_json_(o)   for o in ensure_list(data.get('media'))]
        identifiers = [Identifier._from_json_(o)        for o in ensure_list(data.get('identifiers'))]
        names       = [Name._from_json_(o)              for o in ensure_list(data.get('names'))]
        facts       = [Fact._from_json_(o)              for o in ensure_list(data.get('facts'))]

        # Build the instance
        inst = cls(
            id          = id_,
            lang        = lang,
            sources     = sources,
            analysis    = analysis,
            notes       = notes,
            confidence  = confidence,
            attribution = attribution,
            extracted   = extracted,
            evidence    = evidence,
            media       = media,
            identifiers = identifiers,
            private     = private,
            gender      = gender,
            names       = names,
            facts       = facts,
            living      = living
        )

        return inst
