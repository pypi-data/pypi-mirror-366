from typing import Optional
import json

class Address:
    identifier = "http://gedcomx.org/v1/Address"
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, value: Optional[str] = None,
                 city: Optional[str] = None,
                 country: Optional[str] = None,
                 postalCode: Optional[str] = None,
                 stateOrProvince: Optional[str] = None,
                 street: Optional[str] = None,
                 street2: Optional[str] = None,
                 street3: Optional[str] = None,
                 street4: Optional[str] = None,
                 street5: Optional[str] = None,
                 street6: Optional[str] = None):
        
        self._value = value #TODO impliment a parser for date strings.
        self.city = city
        self.country = country
        self.postalCode = postalCode
        self.stateOrProvince = stateOrProvince
        self.street = street
        self.street2 = street2
        self.street3 = street3
        self.street4 = street4
        self.street5 = street5
        self.street6 = street6

    @property
    def value(self) -> Optional[str]:
        if self._value:
            return self._value
        return ', '.join(filter(None, [
            self._street, self._street2, self._street3,
            self._street4, self._street5, self._street6,
            self._city, self._stateOrProvince,
            self._postalCode, self._country
        ]))
    
         
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        
        return (
            self.value == other.value and
            self.city == other.city and
            self.country == other.country and
            self.postalCode == other.postalCode and
            self.stateOrProvince == other.stateOrProvince and
            self.street == other.street and
            self.street2 == other.street2 and
            self.street3 == other.street3 and
            self.street4 == other.street4 and
            self.street5 == other.street5 and
            self.street6 == other.street6
        )
    
    def __str__(self) -> str:
        # Combine non-empty address components into a formatted string
        parts = [
            self._value,
            self.street,
            self.street2,
            self.street3,
            self.street4,
            self.street5,
            self.street6,
            self.city,
            self.stateOrProvince,
            self.postalCode,
            self.country
        ]

        # Filter out any parts that are None or empty strings
        filtered_parts = [str(part) for part in parts if part]

        # Join the remaining parts with a comma and space
        return ', '.join(filtered_parts)
    
    @property
    def __as_dict__(self):
        return {
            #"value": self._value if self._value else None,
            "city": self.city if self.city else None,
            "country": self.country if self.country else None,
            "postalCode": self.postalCode if self.postalCode else None,
            "stateOrProvince": self.stateOrProvince if self.stateOrProvince else None,
            "street": self.street if self.street else None,
            "street2": self.street2 if self.street2 else None,
            "street3": self.street3 if self.street3 else None,
            "street4": self.street4 if self.street4 else None,
            "street5": self.street5 if self.street5 else None,
            "street6": self.street6 if self.street6 else None
        }


