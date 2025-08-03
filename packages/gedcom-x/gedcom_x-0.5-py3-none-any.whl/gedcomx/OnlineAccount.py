from typing import Optional

from .URI import URI

class OnlineAccount:
    identifier = 'http://gedcomx.org/v1/OnlineAccount'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, serviceHomepage: URI, accountName: str) -> None:
        pass