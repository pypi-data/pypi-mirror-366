from typing import Optional


class DateFormat:
    def __init__(self) -> None:
        pass
        

class Date:
    identifier = 'http://gedcomx.org/v1/Date'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, original: Optional[str],formal: Optional[str | DateFormat] = None) -> None:
        self.orginal = original
        self.formal = formal
    
    def _prop_dict(self):
        return {'original': self.orginal,
                'formal': self.formal}

# Date
Date._from_json_ = classmethod(lambda cls, data: Date(
    original=data.get('original'),
    formal=data.get('formal')
))

Date._to_dict_ = lambda self: {
    'original': self.orginal,
    'formal': self.formal}    