from typing import Optional
from urllib.parse import urlparse

class URI:
    @classmethod
    def from_url(cls, url: str) -> 'URI':
        parsed_url = urlparse(url)
        return cls(
            value=url,
            scheme=parsed_url.scheme if parsed_url.scheme else 'gedcomx',
            authority=parsed_url.netloc,
            path=parsed_url.path,
            query=parsed_url.query,
            fragment=parsed_url.fragment
        )
    
    def parse(value: str) -> None:
        """Parse the URI string and populate attributes."""
        parsed = urlparse(value)
        return URI(scheme=parsed.scheme,authority = parsed.netloc, path = parsed.path, query = parsed.query, fragment = parsed.fragment)
        

    def __init__(self, value: Optional[str] = None,
                 scheme: Optional[str] = None,
                 authority: Optional[str] = None,
                 path: Optional[str] = None,
                 query: Optional[str] = None,
                 fragment: Optional[str] = None,
                 object = None) -> None:
        
        self._scheme = scheme if scheme else 'gedcomx'
        self._authority = authority
        self._path = path
        self._query = query
        self._fragment = fragment
        self._object = None

        if object is not None:
            self._object = object
            if hasattr(object,'_uri'):
                self._object._uri = self


    @property
    def _uri(self) -> str:
        uri = ""
        if self._scheme:
            uri += f"{self._scheme}://"
        if self._authority:
            uri += f"{self._authority}/"
        if self._path:
            uri += f"{self._path}/"
        if self._query:
            uri += f"?{self._query}"
        if self._fragment:
            uri += f"#{self._fragment}"
        return uri
    
    @property
    def value(self):
        return self._uri
    
    @property
    def _as_dict_(self):
        return {"Resource":self._uri}
    
    
    @classmethod
    def _from_json_(obj,text):
        return URI(scheme='NEED TO DEAL WITH URI')