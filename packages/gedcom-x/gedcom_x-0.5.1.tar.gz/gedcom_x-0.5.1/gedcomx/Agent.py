import base64
import uuid

from typing import List, Optional

from .Address import Address
from .Identifier import Identifier
from .OnlineAccount import OnlineAccount
from .TextValue import TextValue
from .URI import URI

class Agent:
    @staticmethod
    def default_id_generator():
        # Generate a standard UUID
        standard_uuid = uuid.uuid4()
        # Convert UUID to bytes
        uuid_bytes = standard_uuid.bytes
        # Encode bytes to a Base64 string
        short_uuid = base64.urlsafe_b64encode(uuid_bytes).rstrip(b'=').decode('utf-8')
        return short_uuid
    
    def __init__(self, id: Optional[str] = None,
                    identifiers: Optional[List[Identifier]] = [], 
                    names: Optional[List[TextValue]] = [], 
                    homepage: Optional[URI] = None, 
                    openid: Optional[URI] = None, 
                    accounts: Optional[List[OnlineAccount]] = [],
                    emails: Optional[List[URI]] = [], 
                    phones: Optional[List[URI]] = [], 
                    addresses: Optional[List[Address]] = [], 
                    person: Optional[object] | Optional[URI] = None, # should be of Type 'Person', 'object' to avoid circular imports
                    uri: URI = None): 
        
        self._id_generator = Agent.default_id_generator

        self.id = id if id else self._id_generator()
        self.identifiers = identifiers
        self.names = names
        self.homepage = homepage
        self.openid = openid
        self.accounts = accounts
        self.emails = emails
        self.phones = phones
        self.addresses = addresses
        
        self._uri = URI(fragment="agent:"+ self.id)
    
    def _append_to_name(self, text_to_append: str):
        self.names[0].value = self.names[0].value + text_to_append

    def add_address(self, address_to_add: Address):
        if address_to_add and isinstance(address_to_add, Address):
            for current_address in self.addresses:
                if address_to_add == current_address:
                    return False
            self.addresses.append(address_to_add)
        else:
            raise ValueError(f"address must be of type Address, not {type(address_to_add)}")
        
    def add_name(self, name_to_add: TextValue):
        if isinstance(name_to_add,str): name_to_add = TextValue(value=name_to_add)
        if name_to_add and isinstance(name_to_add,TextValue):
            for current_name in self.names:
                if name_to_add == current_name:
                    return
            self.names.append(name_to_add)
        else:
            raise ValueError(f'name must be of type str or TextValue, recived {type(name_to_add)}')
    
    @property
    def __as_dict__(self):
        return {
            "id": self.id if self.id else None,
            "identifiers": [identifier.__as_dict__() for identifier in self.identifiers],
            "names": [name._prop_dict() for name in self.names],
            "homepage": self.homepage if self.homepage else None,
            "openid": self.openid if self.openid else None,
            "accounts": self.accounts if self.accounts else None,
            "emails": self.emails if self.emails else None,
            "phones": self.phones if self.phones else None,
            "addresses": [address.__as_dict__ for address in self.addresses]
        }