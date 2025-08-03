from datetime import datetime
from typing import Optional, Dict, Any

from .URI import URI

class Attribution:
    identifier = 'http://gedcomx.org/v1/Attribution'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self,contributor: Optional[URI],
                 modified: Optional[datetime],
                 changeMessage: Optional[str],
                 creator: Optional[URI],
                 created: Optional[datetime]) -> None:
        

        from .Agent import Agent
        self._contributor_object = None
        self.modified = modified
        self.changeMessage = changeMessage
        self.creator = creator
        self.created = created


        if isinstance(contributor,URI):
            # TODO DEAL WITH URI <------------------------------------------------------------------------------------------------------------------
            self._contributor_object = contributor
        elif isinstance(contributor,Agent):
            self._contributor_object = contributor
            if hasattr(contributor,'_uri'):
                self.contributor = contributor._uri
            else:
                assert False
                self.description = URI(object=description)
                description._uri = self.description
                description._object = description
        else:
            raise ValueError(f"'description' must be of type 'SourceDescription' or 'URI', type: {type(contributor)} was provided, with value: {contributor}")
    
    @property
    def _as_dict_(self) -> Dict[str, Any]:
        """
        Serialize Attribution to a JSON-ready dict, skipping None values.
        """
        def _fmt_dt(dt: datetime) -> str:
            # ISO 8601 format
            return dt.isoformat()

        data: Dict[str, Any] = {}
        if self._contributor_object:
            data['contributor'] = (self._contributor_object._as_dict_
                                   if hasattr(self._contributor_object, '_as_dict_') else
                                   None)
        if self.created:
            data['created'] = _fmt_dt(self.created)
        if self.creator:
            data['creator'] = (self.creator._prop_dict()
                                if hasattr(self.creator, '_prop_dict') else
                                self.creator._prop_dict())
        if self.modified:
            data['modified'] = _fmt_dt(self.modified)
        if self.changeMessage is not None:
            data['changeMessage'] = self.changeMessage    
        return data

    @classmethod
    def _from_json_(cls, data: Dict[str, Any]) -> 'Attribution':
        """
        Construct Attribution from a dict (as parsed from JSON).
        Handles 'created' and 'modified' as ISO strings or epoch ms ints.
        """
        # contributor
        contrib = None
        if 'contributor' in data:
            raw = data['contributor']
            if isinstance(raw, dict):
                contrib = URI._from_json_(raw)
            elif isinstance(raw, str):
                contrib = URI(uri=raw)

        # creator
        creat = None
        if 'creator' in data:
            raw = data['creator']
            if isinstance(raw, dict):
                creat = URI._from_json_(raw)
            elif isinstance(raw, str):
                creat = URI(uri=raw)

        # parse created date
        raw_created = data.get('created')
        if isinstance(raw_created, (int, float)):
            created_dt = datetime.fromtimestamp(raw_created / 1000.0)
        elif isinstance(raw_created, str):
            created_dt = datetime.fromisoformat(raw_created)
        else:
            created_dt = None

        # parse modified date
        raw_modified = data.get('modified')
        if isinstance(raw_modified, (int, float)):
            modified_dt = datetime.fromtimestamp(raw_modified / 1000.0)
        elif isinstance(raw_modified, str):
            modified_dt = datetime.fromisoformat(raw_modified)
        else:
            modified_dt = None

        change_msg = data.get('changeMessage')

        return cls(
            contributor=contrib,
            created=created_dt,
            creator=creat,
            modified=modified_dt,
            changeMessage=change_msg
        )
