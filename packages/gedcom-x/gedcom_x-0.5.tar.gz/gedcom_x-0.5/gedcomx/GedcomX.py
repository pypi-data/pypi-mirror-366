DEBUG = False
import base64
import json
import mimetypes
import re
import uuid
import xml.etree.ElementTree as ET

from typing import List, Optional
from xml.dom import minidom
from .Address import Address
from .Agent import Agent
from .Attribution import Attribution
from .Conclusion import Conclusion
from .Coverage import Coverage
from .Date import Date
from .Document import Document
from .EvidenceReference import EvidenceReference
from .Event import Event,EventType,EventRole,EventRoleType
from .Fact import Fact, FactType, FactQualifier
from .Gedcom import Gedcom
from .Gedcom import GedcomRecord
from .Gender import Gender, GenderType
from .Group import Group
from .Identifier import Identifier, IdentifierType
from .Name import Name, NameType, NameForm, NamePart, NamePartType, NamePartQualifier
from .Note import Note
from .OnlineAccount import OnlineAccount
from .Person import Person
from .PlaceDescription import PlaceDescription
from .PlaceReference import PlaceReference
from .Qualifier import Qualifier
from .Relationship import Relationship, RelationshipType
from .SourceCitation import SourceCitation
from .SourceDescription import SourceDescription, ResourceType
from .SourceReference import SourceReference, KnownSourceReference
from .Subject import Subject
from .TextValue import TextValue
from .TopLevelTypeCollection import TopLevelTypeCollection
from .URI import URI

def TypeCollection(item_type):
    class Collection:
        def __init__(self):
            self._items = []
            self._id_index = {}
            self._name_index = {}
            self._uri_index = {}
            self.uri = URI(path=f'/{item_type.__name__}s/')

        def __iter__(self):
            self._index = 0
            return self

        def __next__(self):
            if self._index < len(self._items):
                result = self._items[self._index]
                self._index += 1
                return result
            else:
                raise StopIteration

        @property
        def item_type(self):
            return item_type
        
        def _update_indexes(self, item):
            # Update the id index
            if hasattr(item, 'id'):
                self._id_index[item.id] = item
            
            try:
                if hasattr(item, '_uri'):
                    self._uri_index[item._uri.value] = item
            except AttributeError as e:
                print(f"type{item}")
                assert False

            # Update the name index
            ''' #TODO Fix name handling on persons
            if hasattr(item, 'names'):
                names = getattr(item, 'names')
                for name in names:
                    print(name._as_dict_)
                    name_value = name.value if isinstance(name, TextValue) else name
                    if name_value in self._name_index:
                        self._name_index[name_value].append(item)
                    else:
                        self._name_index[name_value] = [item]
            '''

        def _remove_from_indexes(self, item):
            # Remove from the id index
            if hasattr(item, 'id'):
                if item.id in self._id_index:
                    del self._id_index[item.id]

            # Remove from the name index
            if hasattr(item, 'names'):
                names = getattr(item, 'names')
                for name in names:
                    name_value = name.value if isinstance(name, TextValue) else name
                    if name_value in self._name_index:
                        if item in self._name_index[name_value]:
                            self._name_index[name_value].remove(item)
                            if not self._name_index[name_value]:
                                del self._name_index[name_value]

        def byName(self, sname: str):
            # Use the name index for fast lookup
            sname = sname.strip()
            return self._name_index.get(sname, [])

        def byId(self, id):
            # Use the id index for fast lookup
            return self._id_index.get(id, None)
        
        def byUri(self, uri):
            # Use the id index for fast lookup
            return self._uri_index.get(uri.value, None)

        def append(self, item):
            if not isinstance(item, item_type):
                raise TypeError(f"Expected item of type {item_type.__name__}, got {type(item).__name__}")
            item._uri._path  = f'{str(item_type.__name__)}s' if item._uri._path is None else item._uri._path
            #if isinstance(item,Agent):
            #    item._uri._path  = 'Agents'
            #    print(item._uri._as_dict_)
                
            self._items.append(item)
            self._update_indexes(item)

        def remove(self, item):
            if item not in self._items:
                raise ValueError("Item not found in the collection.")
            self._items.remove(item)
            self._remove_from_indexes(item)

        def __repr__(self):
            return f"Collection({self._items!r})"
        
        def list(self):
            for item in self._items:
                print(item)
        
        def __call__(self, **kwargs):
            results = []
            for item in self._items:
                match = True
                for key, value in kwargs.items():
                    if not hasattr(item, key) or getattr(item, key) != value:
                        match = False
                        break
                if match:
                    results.append(item)
            return results
        
        def __len__(self):
            return len(self._items)
        
        def __getitem__(self, index):
            return self._items[index]
    
        @property
        def _items_as_dict(self) -> dict:
            print(self.item_type)
                        
            #return {f'{str(item_type.__name__)}s': [item._as_dict_ for item in self._items]}
            return {f'{str(item_type.__name__)}s': [item._as_dict_ for item in self._items]}
        
        @property
        def json(self):
            return json.dumps(self._as_dict, indent=4)

        @property
        def _as_dict_(self):
            return {"Collection": [item._as_dict_ for item in self._items]}         

    return Collection()

class GedcomX:
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, id: str = None, attribution: Attribution = None, filepath: str = None) -> None:
        self.id = id
        self.attribution = attribution

        self._filepath = None
        
        self.source_descriptions = TypeCollection(SourceDescription)
        self.persons = TypeCollection(Person)
        self.relationships = TypeCollection(Relationship)      
        self.agents = TypeCollection(Agent)
        self.events = TypeCollection(Event)
        self.documents = TypeCollection(Document)
        self.places = TypeCollection(PlaceDescription)
        self.groups = TypeCollection(Group)

        self.person_relationships_lookup = {}

    def _add(self,gedcomx_type_object):
        #print(type(gedcomx_type_object))
        if gedcomx_type_object:
            if isinstance(gedcomx_type_object,Person):
                self.add_person(gedcomx_type_object)
            elif isinstance(gedcomx_type_object,SourceDescription):
                self.add_source_description(gedcomx_type_object)
            elif isinstance(gedcomx_type_object,Agent):
                self.add_agent(gedcomx_type_object)
            elif isinstance(gedcomx_type_object,PlaceDescription):
                self.add_place_description(gedcomx_type_object)
            elif isinstance(gedcomx_type_object,Event):
                self.add_event(gedcomx_type_object)
            elif isinstance(gedcomx_type_object,Relationship):
                self.add_relationship(gedcomx_type_object)
            else:
                raise ValueError(f"I do not know how to add an Object of type {type(gedcomx_type_object)}")
        else:
            Warning("Tried to add a None type to the Geneology")

    def add_source_description(self,sourceDescription: SourceDescription):
        if sourceDescription and isinstance(sourceDescription,SourceDescription):
            if sourceDescription.id is None:
                sourceDescription.id =self.default_id_generator()
            self.source_descriptions.append(item=sourceDescription)
            self.lastSourceDescriptionAdded = sourceDescription
        else:
            raise ValueError(f"When adding a SourceDescription, value must be of type SourceDescription, type {type(sourceDescription)} was provided")

    def add_person(self,person: Person):
        if person and isinstance(person,Person):
            if person.id is None:
                person.id =self.personURIgenerator()
            self.persons.append(item=person)
        else:
            raise ValueError()
        
    def add_relationship(self,relationship: Relationship):
        if relationship and isinstance(relationship,Relationship):
            if isinstance(relationship.person1,URI) and isinstance(relationship.person2,URI):
                print("Adding unresolved Relationship")
                self.relationships.append(relationship)
                return

            if relationship.person1:
                if relationship.person1.id is None:
                    relationship.person1.id = self.personURIgenerator()
                if not self.persons.byId(relationship.person1.id):
                    self.persons.append(relationship.person1)
                if relationship.person1.id not in self.person_relationships_lookup:
                    self.person_relationships_lookup[relationship.person1.id] = []
                self.person_relationships_lookup[relationship.person1.id].append(relationship)
                relationship.person1._add_relationship(relationship)
            else:
                raise ValueError
            
            if relationship.person2:
                if relationship.person2.id is None:
                    relationship.person2.id = self.personURIgenerator() #TODO
                if not self.persons.byId(relationship.person2.id):
                    self.persons.append(relationship.person2)
                if relationship.person2.id not in self.person_relationships_lookup:
                    self.person_relationships_lookup[relationship.person2.id] = []
                self.person_relationships_lookup[relationship.person2.id].append(relationship)
                relationship.person2._add_relationship(relationship)
            else:
                raise ValueError

            self.relationships.append(relationship)
        else:
            raise ValueError()
    
    def add_place_description(self,placeDescription: PlaceDescription):
        if placeDescription and isinstance(placeDescription,PlaceDescription):
            if placeDescription.id is None:
                placeDescription.id = self.PlaceDescriptionURIGenerator()
            self.places.append(placeDescription)

    def add_agent(self,agent: Agent):
        if agent and isinstance(agent,Agent):
            if agent.id is None:
                raise("Empty ID")
                agent.id = Agent.default_id_generator()
            if self.agents.byId(agent.id):
                raise ValueError
            print(f'Added Agent with id: {agent.id}')
            self.agents.append(agent)
    
    def add_event(self,event_to_add: Event):
        if event_to_add and isinstance(event_to_add,Event):
            for current_event in self.events:
                if event_to_add == current_event:
                    return
            self.events.append(event_to_add)

    def person(self,id: str):
        filtered = [person for person in self.persons if getattr(person, 'id') == id]
        if filtered: return filtered[0]
        return None
    
    def source(self,id: str):
        filtered = [source for source in self.source_descriptions if getattr(source, 'id') == id]
        if filtered: return filtered[0]
        return None        


class Translater():
    def __init__(self,gedcom) -> None:
        self.handlers = {}
        self.gedcom: Gedcom = gedcom if gedcom else None
        self.gedcomx = GedcomX()
        
        self.object_stack = []
        self.object_map = {}
        self.missing_handler_count = {}

        self.translate()

    gedcom_even_to_fact = {
    # Person Fact Types
    "ADOP": FactType.Adoption,
    "CHR": FactType.AdultChristening,
    "EVEN": FactType.Amnesty,  # and other FactTypes with no direct GEDCOM tag
    "BAPM": FactType.Baptism,
    "BARM": FactType.BarMitzvah,
    "BASM": FactType.BatMitzvah,
    "BIRT": FactType.Birth,
    "BIRT, CHR": FactType.Birth,
    "BLES": FactType.Blessing,
    "BURI": FactType.Burial,
    "CAST": FactType.Caste,
    "CENS": FactType.Census,
    "CIRC": FactType.Circumcision,
    "CONF": FactType.Confirmation,
    "CREM": FactType.Cremation,
    "DEAT": FactType.Death,
    "EDUC": FactType.Education,
    "EMIG": FactType.Emigration,
    "FCOM": FactType.FirstCommunion,
    "GRAD": FactType.Graduation,
    "IMMI": FactType.Immigration,
    "MIL": FactType.MilitaryService,
    "NATI": FactType.Nationality,
    "NATU": FactType.Naturalization,
    "OCCU": FactType.Occupation,
    "ORDN": FactType.Ordination,
    "DSCR": FactType.PhysicalDescription,
    "PROB": FactType.Probate,
    "PROP": FactType.Property,
    "RELI": FactType.Religion,
    "RESI": FactType.Residence,
    "WILL": FactType.Will,

    # Couple Relationship Fact Types
    "ANUL": FactType.Annulment,
    "DIV": FactType.Divorce,
    "DIVF": FactType.DivorceFiling,
    "ENGA": FactType.Engagement,
    "MARR": FactType.Marriage,
    "MARB": FactType.MarriageBanns,
    "MARC": FactType.MarriageContract,
    "MARL": FactType.MarriageLicense,
    "SEPA": FactType.Separation,

    # Parent-Child Relationship Fact Types
    # (Note: Only ADOPTION has a direct GEDCOM tag, others are under "EVEN")
    "ADOP": FactType.AdoptiveParent
}
    
    
    def clean_str(text: str) -> str:
        # Regular expression to match HTML/XML tags
        clean_text = re.sub(r'<[^>]+>', '', text)
        
        return clean_text

    def translate(self):
        for repository in self.gedcom.repositories:
            self.parse_record(repository)
        print(f"Translated {len(self.gedcomx.agents)} 'REPO' records to Agents")
        for source in self.gedcom.sources:
            self.parse_record(source)
        print(f"Translated {len(self.gedcomx.source_descriptions)} 'SOUR' records to SourceDescription")

        for object in self.gedcom.objects:
            self.parse_record(object)
        print(f"Translated {len(self.gedcom.objects)} 'OBJE' records to SourceDescriptions")

        for individual in self.gedcom.individuals:
            self.parse_record(individual)
        print(f"Translated {len(self.gedcomx.persons)} 'INDI' records to Persons")

        for key in self.missing_handler_count:
            print(f"{key}: {self.missing_handler_count[key]}")

        

        fam_count = len(self.gedcom.families)
        for family in self.gedcom.families:
            self.handle_fam(family)
        print(f"Translated {fam_count} 'FAM' records to {len(self.gedcomx.relationships)} Relationship")
        
        print(f"Translated {len(self.gedcomx.events)} 'EVEN' records to Events")

    def find_urls(sef,text: str):
        # Regular expression pattern to match URLs
        url_pattern = re.compile(r'https?://[^\s]+')
        # Find all URLs using the pattern
        urls = url_pattern.findall(text)
        return urls

    @property
    def event_type_conversion_table(self):
        return {'BIRT':EventType.BIRTH,
                'OBIT':FactType.OBITUARY}
       
    def parse_record(self,record: GedcomRecord):
        
        if DEBUG: print(record.describe())
        handler_name = 'handle_' + record.tag.lower()
        
        if hasattr(self,handler_name):
            
            handler = getattr(self,handler_name)
            handler(record)
        else:
            if record.tag in self.missing_handler_count:
                self.missing_handler_count[record.tag] += 1
            else:
                self.missing_handler_count[record.tag] = 1
                if not record.tag.startswith("_"):
                    print(f"\033[1;31mCould not find handler for GEDCOM tag {record.tag}\n{record.describe()}\033[0m")
        for sub_record in record.subRecords():
            self.parse_record(sub_record)

    def handle__apid(self, record):
        if isinstance(self.object_map[record.level-1], SourceReference):
            self.object_map[record.level-1]._description_object.add_identifier(Identifier(value=URI.from_url('APID://' + record.value)))
        elif isinstance(self.object_map[record.level-1], SourceDescription):
            self.object_map[record.level-1].add_identifier(Identifier(value=URI.from_url('APID://' + record.value)))
        else:
            raise ValueError(f"Could not handle '_APID' tag in record {record.describe()}, last stack object {type(self.object_map[record.level-1])}")

    def handle__meta(self, record):
        if isinstance(self.object_map[record.level-1], SourceDescription):
            gxobject = Note(text=Translater.clean_str(record.value))
            self.object_map[record.level-1].add_note(gxobject)
            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        else:
            raise ValueError(f"Could not handle 'WWW' tag in record {record.describe()}, last stack object {self.object_map[record.level-1]}")

    def handle__wlnk(self, record):
        return self.handle_sour(record)

    def handle_addr(self, record):
        if isinstance(self.object_map[record.level-1], Agent):
            # TODO CHeck if URL?
            if Translater.clean_str(record.value):
                gxobject = URI(value=Translater.clean_str(record.value))
            else:
                gxobject = Address()
            self.object_map[record.level-1].address = gxobject
            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        else:
            raise ValueError(f"I do not know how to handle an 'ADDR' tag for a {type(self.object_map[record.level-1])}")
    
    def handle_adr1(self, record):
        if isinstance(self.object_map[record.level-1], Address):
            if Translater.clean_str(record.value):
                self.object_map[record.level-1].street = Translater.clean_str(record.value)
                
        else:
            raise ValueError(f"I do not know how to handle an 'ADDR' tag for a {type(self.object_map[record.level-1])}")

    def handle_adop(self, record):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Fact(type=FactType.ADOPTION)
            self.object_map[record.level-1].add_fact(gxobject)

            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        else:
            print("Cannot translate 'BAPM")
            assert False

    def handle_auth(self, record):
        if isinstance(self.object_map[record.level-1], SourceDescription):
            if self.gedcomx.agents.byName(record.value):
                gxobject = self.gedcomx.agents.byName(record.value)[0]
            else:
                gxobject = Agent(names=[TextValue(record.value)])
                self.gedcomx.add_agent(gxobject)
            
            self.object_map[record.level-1].author = gxobject
            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        else:
            print("Cannot translate 'AUTH")
            assert False

    def handle_bapm(self, record):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Fact(type=FactType.Baptism)
            self.object_map[record.level-1].add_fact(gxobject)

            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        else:
            print("Cannot translate 'BAPM")
            assert False

    def handle_birt(self, record):
        if isinstance(self.object_map[record.level-1], Person):
            #gxobject = Event(type=EventType.BIRTH, roles=[EventRole(person=self.object_map[record.level-1], type=EventRoleType.Principal)])
            gxobject = Fact(type=FactType.Birth)
            #self.gedcomx.add_event(gxobject)
            self.object_map[record.level-1].add_fact(gxobject)

            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        else:
            print("Cannot translate 'AUTH")
            assert False

    def handle_buri(self, record):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Fact(type=FactType.Burial)
            self.object_map[record.level-1].add_fact(gxobject)

            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        else:
            print("Cannot translate 'BURI")
            assert False

    def handle_caln(self, record):
        if isinstance(self.object_map[record.level-1], SourceReference):
            self.object_map[record.level-1].description.add_identifier(Identifier(value=URI.from_url('Call Number:' + record.value)))
        elif isinstance(self.object_map[record.level-1], SourceDescription):
            self.object_map[record.level-1].add_identifier(Identifier(value=URI.from_url('Call Number:' + record.value)))
        elif isinstance(self.object_map[record.level-1], Agent):
            pass
            # TODO Why is GEDCOM so shitty? A callnumber for a repository?
        else:
            raise ValueError(f"Could not handle 'CALN' tag in record {record.describe()}, last stack object {type(self.object_map[record.level-1])}")

    def handle_chr(self, record):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Fact(type=FactType.Christening)
            self.object_map[record.level-1].add_fact(gxobject)

            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        else:
            print("Cannot translate 'CHR")
            assert False

    def handle_city(self, record):
        if isinstance(self.object_map[record.level-1], Address):
            self.object_map[record.level-1].city = Translater.clean_str(record.value)
        else:
            raise ValueError(f"I do not know how to handle an 'CITY' tag for a {type(self.object_map[record.level-1])}")
        
    def handle_conc(self, record):
        if isinstance(self.object_map[record.level-1], Note):
            gxobject = Translater.clean_str(str(record.value))
            self.object_map[record.level-1].append(gxobject)
        elif isinstance(self.object_map[record.level-1], Agent):
            gxobject = str(record.value)
            self.object_map[record.level-1]._append_to_name(gxobject)
        elif isinstance(self.object_map[record.level-1], Qualifier):
            gxobject = str(record.value)
            self.object_map[record.level-2].append(gxobject)
        elif isinstance(self.object_map[record.level-1], TextValue):
            #gxobject = TextValue(value=Translater.clean_str(record.value))
            self.object_map[record.level-1]._append_to_value(record.value)
        elif isinstance(self.object_map[record.level-1], SourceReference):
            self.object_map[record.level-1].append(record.value)
        elif isinstance(self.object_map[record.level-1], Fact):
            self.object_map[record.level-1].notes[0].text += record.value
            
        else:
            print(f"Cannot translate 'CONC', {self.object_map[record.level-1]}")
            assert False

    def handle_cont(self, record):
        if isinstance(self.object_map[record.level-1], Note):
            gxobject = str("\n" + record.value)
            self.object_map[record.level-1].append(gxobject)
        elif isinstance(self.object_map[record.level-1], Agent):
            gxobject = str("\n" + record.value)
        elif isinstance(self.object_map[record.level-1], Qualifier):
            gxobject = str("\n" + record.value)
            self.object_map[record.level-1].append(gxobject)
        elif isinstance(self.object_map[record.level-1], TextValue):
            #gxobject = TextValue(value="\n" + record.value)
            self.object_map[record.level-1]._append_to_value(record.value)
        elif isinstance(self.object_map[record.level-1], SourceReference):
            self.object_map[record.level-1].append(record.value)
        else:
            print(f"Cannot translate 'CONT', {type(self.object_map[record.level-1])}")
            assert False
    
    def handle__crea(self, record):
        if isinstance(self.object_map[record.level-1], SourceDescription):
            self.object_map[record.level-1].created = Date(original=record.value)
        else:
            raise ValueError(f"Could not handle '_URL' tag in record {record.describe()}, last stack object {self.object_map[record.level-1]}")
    
    def handle_ctry(self, record):
        if isinstance(self.object_map[record.level-1], Address):
            self.object_map[record.level-1].country = Translater.clean_str(record.value)
        else:
            raise ValueError(f"I do not know how to handle an 'CTRY' tag for a {type(self.object_map[record.level-1])}")
     
    def handle_data(self, record: GedcomRecord) -> None:
        if record.value != '':
            assert False
        self.object_map[record.level] = None

    def handle_date(self, record: GedcomRecord):
        if record.parent.tag == 'PUBL':
            gxobject = Date(original=record.value)
            self.object_map[0].published = gxobject

            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        elif isinstance(self.object_map[record.level-1], Event):
            self.object_map[record.level-1].date = Date(original=record.value)
        elif isinstance(self.object_map[record.level-1], Fact):
            self.object_map[record.level-1].date = Date(original=record.value)
        elif record.parent.tag == 'DATA' and isinstance(self.object_map[record.level-2], SourceReference):
            gxobject = Note(text='Date: ' + record.value)
            self.object_map[record.level-2]._description_object.add_note(gxobject)
            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        elif isinstance(self.object_map[record.level-1], SourceDescription):
            
            self.object_map[record.level-1].ctreated = record.value #TODO String to timestamp
            
        else:
            print(f"Cannot translate 'DATE {type(self.object_map[record.level-1])}")
            assert False

    def handle_deat(self, record):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Fact(type=FactType.Death)
            self.object_map[record.level-1].add_fact(gxobject)

            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        else:
            print("Cannot translate 'DEAT")
            assert False

    def handle_even(self, record: GedcomRecord):
        # TODO If events in a @S, check if only 1 person matches?
        if not record.value.strip() == '':
            values = [value.strip() for value in record.value.split(",")]
            for value in values:
                if value in Translater.gedcom_even_to_fact.keys():
                    if isinstance(self.object_map[record.level-1], Person):
                        gxobject = Fact(type=Translater.gedcom_even_to_fact[value])
                        self.object_map[record.level-1].add_fact(gxobject)

                        self.object_stack.append(gxobject)
                        self.object_map[record.level] = gxobject
                        print(self.object_map)
                    else:
                        print(record.describe())
                        assert False
                        # TODO: Fix, this. making an event to cacth subtags, why are these fact tied to a source? GEDCOM is horrible
                        gxobject = Event(type=EventType.UNKNOWN)
                        self.object_stack.append(gxobject)
                        self.object_map[record.level] = gxobject
                else:
                    

                    print("This event does not look like a Fact")

        else:
            possible_fact = FactType.guess(record.subRecord('TYPE')[0].value)
            if possible_fact:
                gxobject = Fact(type=possible_fact)
                self.object_map[record.level-1].add_fact(gxobject)

                self.object_stack.append(gxobject)
                self.object_map[record.level] = gxobject
                return
            elif EventType.guess(record.subRecord('TYPE')[0].value):
                if isinstance(self.object_map[record.level-1], Person):
                    gxobject = Event(type=EventType.guess(record.subRecord('TYPE')[0].value), roles=[EventRole(person=self.object_map[record.level-1], type=EventRoleType.Principal)])
                    self.gedcomx.add_event(gxobject)
                    self.object_stack.append(gxobject)
                    self.object_map[record.level] = gxobject
                return
            else:
                if isinstance(self.object_map[record.level-1], Person):
                    gxobject = Event(type=None, roles=[EventRole(person=self.object_map[record.level-1], type=EventRoleType.Principal)])
                    gxobject.add_note(Note(subject='Event', text=record.value))
                    self.gedcomx.add_event(gxobject)
                    self.object_stack.append(gxobject)
                    self.object_map[record.level] = gxobject
                    return
                    
                else:
                    assert False

    def handle_fam(self, record: GedcomRecord) -> None:
        if record.tag != 'FAM' or record.level != 0:
            raise ValueError("Invalid record: Must be a level 0 FAM record")

        husband, wife, children = None, None, []

        husband_record = record.subRecords('HUSB')
        if husband_record:
            husband = self.gedcomx.person(husband_record[0].value.replace('@',''))

        wife_record = record.subRecords('WIFE')
        if wife_record:
            wife = self.gedcomx.person(wife_record[0].value.replace('@',''))

        children_records = record.subRecords('CHIL')
        if children_records:
            for child_record in children_records:
                child = self.gedcomx.person(child_record.value.replace('@',''))
                if child:
                    children.append(child)

        if husband:
            for child in children:
                relationship = Relationship(person1=husband, person2=child, type=RelationshipType.ParentChild)
                self.gedcomx.add_relationship(relationship)
        if wife:
            for child in children:
                relationship = Relationship(person1=wife, person2=child, type=RelationshipType.ParentChild)
                self.gedcomx.add_relationship(relationship)
        if husband and wife:
            relationship = Relationship(person1=husband, person2=wife, type=RelationshipType.Couple)
            self.gedcomx.add_relationship(relationship)

    def handle_famc(self, record: GedcomRecord) -> None:
        return

    def handle_fams(self, record: GedcomRecord) -> None:
        return

    def handle_file(self, record: GedcomRecord):
        if record.value.strip() != '':
            #raise ValueError(f"I did not expect the 'FILE' tag to have a value: {record.value}")
            #TODO Handle files referenced here
            ...
        elif isinstance(self.object_map[record.level-1], SourceDescription):
            ...
        self.object_map[record.level-1].resourceType = ResourceType.DigitalArtifact
            

    def handle_form(self, record: GedcomRecord):
        if record.parent.tag == 'FILE' and isinstance(self.object_map[record.level-2], SourceDescription):
            if record.value.strip() != '':
                mime_type, _ = mimetypes.guess_type('placehold.' + record.value)
                if mime_type:
                    self.object_map[record.level-2].mediaType = mime_type
                else:
                    print(f"Could not determing mime type from {record.value}")
        else:
            raise ValueError(f"I do not know how to translate the 'FORM' tag with value '{record.value}' for a {type(self.object_map[record.level-1])}")

    def handle_givn(self, record):
        if isinstance(self.object_map[record.level-1], Name):
            given_name = NamePart(value=record.value, type=NamePartType.Given)
            self.object_map[record.level-1]._add_name_part(given_name)
        else:
            print(f"{record.describe()}, Cannot translate 'NAME', {self.object_map[record.level-1]}")
            assert False

    def handle_indi(self, record):
        person = Person(id=record.xref.replace('@',''))
        self.gedcomx.add_person(person)
        self.object_stack.append(person)
        self.object_map[record.level] = person

    def handle_immi(self, record):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Fact(type=FactType.Immigration)
            self.object_map[record.level-1].add_fact(gxobject)

            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        else:
            print("Cannot translate 'IMMI")
            assert False

    def handle_marr(self, record):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Fact(type=FactType.Marriage)
            self.object_map[record.level-1].add_fact(gxobject)

            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        else:
            print("Cannot translate 'MARR")
            assert False

    def handle_name(self, record):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Name.simple(record.value)
            #gxobject = Name(nameForms=[NameForm(fullText=record.value)], type=NameType.BirthName)
            self.object_map[record.level-1].add_name(gxobject)

            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        elif isinstance(self.object_map[record.level-1], Agent):
            gxobject = TextValue(value=record.value)
            self.object_map[record.level-1].add_name(gxobject)
        else:
            print(f"{record.describe()}, Cannot translate 'NAME', {self.object_map[record.level-1]}")
            assert False

    def handle_note(self, record):
        if isinstance(self.object_map[record.level-1], SourceDescription):
            gxobject = Note(text=Translater.clean_str(record.value))
            self.object_map[record.level-1].add_note(gxobject)

            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        elif isinstance(self.object_map[record.level-1], SourceReference):
            gxobject = Note(text=Translater.clean_str(record.value))
            self.object_map[record.level-1]._description_object.add_note(gxobject)

            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        elif isinstance(self.object_map[record.level-1], Conclusion):
            gxobject = Note(text=record.value)
            self.object_map[record.level-1].add_note(gxobject)

            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        else:
            raise ValueError(f"Could not handle 'NOTE' tag in record {record.describe()}, last stack object {type(self.object_map[record.level-1])}")
            assert False

    def handle_nsfx(self, record):
        if isinstance(self.object_map[record.level-1], Name):
            surname = NamePart(value=record.value, type=NamePartType.Suffix)
            self.object_map[record.level-1]._add_name_part(surname)
        else:
            print(f"{record.describe()}, Cannot translate 'NSFX', {self.object_map[record.level-1]}")
            assert False

    def handle_occu(self, record):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Fact(type=FactType.Occupation)
            self.object_map[record.level-1].add_fact(gxobject)

            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        else:
            print("Cannot translate 'OCCU")
            assert False

    def handle_obje(self, record: GedcomRecord):
        self.handle_sour(record)

    def handle_page(self, record):
        if isinstance(self.object_map[record.level-1], SourceReference):
            self.object_map[record.level-1].descriptionId = record.value
            self.object_map[record.level-1].add_qualifier(KnownSourceReference.Page)
            
            #self.object_stack.append(gxobject)
            #self.object_map[record.level] = gxobject
            self.object_map[record.level] = self.object_map[record.level-1]
        else:
            raise ValueError(f"Could not handle 'PAGE' tag in record {record.describe()}, last stack object {self.object_map[record.level-1]}")

    def handle_plac(self, record):
        if isinstance(self.object_map[record.level-1], Agent):
            gxobject = Address(value=record.value)
            self.object_map[record.level-1].add_address(gxobject)

            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        elif isinstance(self.object_map[record.level-1], Event):
            if self.gedcomx.places.byName(record.value):
                self.object_map[record.level-1].place = PlaceReference(original=record.value, descriptionRef=self.gedcomx.places.byName(record.value)[0])
            else:
                place_des = PlaceDescription(names=[TextValue(value=record.value)])
                self.gedcomx.add_place_description(place_des)
                self.object_map[record.level-1].place = PlaceReference(original=record.value, descriptionRef=place_des)
        elif isinstance(self.object_map[record.level-1], Fact):
            if self.gedcomx.places.byName(record.value):
                self.object_map[record.level-1].place = PlaceReference(original=record.value, descriptionRef=self.gedcomx.places.byName(record.value)[0])
            else:
                place_des = PlaceDescription(names=[TextValue(value=record.value)])
                self.gedcomx.add_place_description(place_des)
                self.object_map[record.level-1].place = PlaceReference(original=record.value, descriptionRef=place_des)
        elif isinstance(self.object_map[record.level-1], SourceDescription):
            gxobject = Note(text='Place: ' + record.value)
            self.object_map[record.level-1].add_note(gxobject)
            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        else:
            print("Cannot translate 'PLACE")
            assert False

    def handle_post(self, record):
        if isinstance(self.object_map[record.level-1], Address):
            self.object_map[record.level-1].postalCode = Translater.clean_str(record.value)
        else:
            raise ValueError(f"I do not know how to handle an 'POST' tag for a {type(self.object_map[record.level-1])}")   
    
    def handle_publ(self, record):
        if isinstance(self.object_map[record.level-1], SourceDescription):
            if self.gedcomx.agents.byName(record.value):
                gxobject = self.gedcomx.agents.byName(record.value)[0]
            else:
                gxobject = Agent(names=[TextValue(record.value)])
                self.gedcomx.add_agent(gxobject)
            self.object_map[record.level-1].publisher = gxobject

            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        else:
            print("Cannot translate 'PUBL")
            assert False

    def handle_prob(self, record):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Fact(type=FactType.Probate)
            self.object_map[record.level-1].add_fact(gxobject)

            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        else:
            print("Cannot translate 'PROB")
            assert False

    def handle_refn(self, record):
        if isinstance(self.object_map[record.level-1], Person) or isinstance(self.object_map[record.level-1], SourceDescription):
            self.object_map[record.level-1].add_identifier(Identifier(value=URI.from_url('Reference Number:' + record.value)))
        else:
            raise ValueError(f"Could not handle 'REFN' tag in record {record.describe()}, last stack object {type(self.object_map[record.level-1])}")

    def handle_repo(self, record):
        if record.level == 0:
            
            gxobject = Agent(id=record.value.replace('@',''))
            self.gedcomx.add_agent(gxobject)
            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
            
        elif isinstance(self.object_map[record.level-1], SourceDescription):
            if self.gedcomx.agents.byId(record.value.replace('@','')):
                # TODO WHere and what to add this to?
                gxobject = self.gedcomx.agents.byId(record.value)
                self.object_map[record.level-1].repository = gxobject
            else:
                print(record.describe())
                raise ValueError()
                gxobject = Agent(names=[TextValue(record.value)])
        else:
            raise ValueError(f"I do not know how to handle 'REPO' tag that is not a top-level, or sub-tag of {type(self.object_map[record.level-1])}")
            

        self.object_stack.append(gxobject)
        self.object_map[record.level] = gxobject

    def handle_resi(self, record):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Fact(type=FactType.Residence)
            if record.value.strip() != '':
                gxobject.add_note(Note(text=record.value))
            self.object_map[record.level-1].add_fact(gxobject)

            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        else:
            print("Cannot translate 'RESI")
            assert False

    def handle_rin(self, record):
        if isinstance(self.object_map[record.level-1], SourceDescription):
            self.object_map[record.level-1].id = record.value
            self.object_map[record.level-1].add_note(Note(text=f"Source had RIN: of {record.value}"))

        else:
            raise ValueError(f"Could not handle 'RIN' tag in record {record.describe()}, last stack object {type(self.object_map[record.level-1])}")
        
    def handle_sex(self, record: GedcomRecord):
        
        if isinstance(self.object_map[record.level-1], Person):
            if record.value == 'M':
                gxobject = Gender(type=GenderType.Male)
            elif record.value == 'F':
                gxobject = Gender(type=GenderType.Female)
            else:
                gxobject = Gender(type=GenderType.Unknown)
            self.object_map[record.level-1].gender = gxobject
            
            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        else:
            assert False

    def handle_sour(self, record):
        if record.level == 0 or record.tag == '_WLNK' or (record.level == 0 and record.tag == 'OBJE'):
            source_description = SourceDescription(id=record.xref)
            self.gedcomx.add_source_description(source_description)
            self.object_stack.append(source_description)
            self.object_map[record.level] = source_description
        else:
            if self.gedcomx.source_descriptions.byId(record.xref):
                gxobject = SourceReference(descriptionId=record.xref, description=self.gedcomx.source_descriptions.byId(record.xref))
            else:
                source_description = SourceDescription(id=record.xref)
                gxobject = SourceReference(descriptionId=record.value, description=source_description)
                if isinstance(self.object_map[record.level-1],SourceReference):
                    self.object_map[record.level-1]._description_object.add_source(gxobject)
                else:
                    self.object_map[record.level-1].add_source(gxobject)
            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
            

    def handle_stae(self, record):
        if isinstance(self.object_map[record.level-1], Address):
            self.object_map[record.level-1].stateOrProvince = Translater.clean_str(record.value)
        else:
            raise ValueError(f"I do not know how to handle an 'STAE' tag for a {type(self.object_map[record.level-1])}")
        
    def handle_surn(self, record):
        if isinstance(self.object_map[record.level-1], Name):
            surname = NamePart(value=record.value, type=NamePartType.Surname)
            self.object_map[record.level-1]._add_name_part(surname)
        else:
            print(f"{record.describe()}, Cannot translate 'NAME', {self.object_map[record.level-1]}")
            assert False

    def handle_text(self, record: GedcomRecord):
        if record.parent.tag == 'DATA':
            if isinstance(self.object_map[record.level-2], SourceReference):
                gxobject = TextValue(value=record.value)
                self.object_map[record.level-2]._description_object.add_description(gxobject)
                self.object_stack.append(gxobject)
                self.object_map[record.level] = gxobject
        else:
            assert False

    def handle_titl(self, record):
        if isinstance(self.object_map[record.level-1], SourceDescription):
            
            gxobject = TextValue(value=Translater.clean_str(record.value))
            self.object_map[record.level-1].add_title(gxobject)

            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        
        elif record.parent.tag == 'FILE' and isinstance(self.object_map[record.level-2], SourceDescription):
            gxobject = TextValue(value=record.value)
            self.object_map[record.level-2].add_title(gxobject)

            self.object_stack.append(gxobject)
            self.object_map[record.level] = gxobject
        elif self.object_map[record.level] and isinstance(self.object_map[record.level], Name):
            gxobject = NamePart(value=record.value, qualifiers=[NamePartQualifier.Title])

            self.object_map[record.level]._add_name_part(gxobject)
        else:
            print(self.object_map)
            print(self.object_map[record.level])
            raise ValueError(f"Could not handle 'TITL' tag in record {record.describe()}, last stack object {type(self.object_map[record.level-1])}")
            assert False

    def handle_type(self, record):
        # peek to see if event or fact
        if isinstance(self.object_map[record.level-1], Event):
            if EventType.guess(record.value):
                self.object_map[record.level-1].type = EventType.guess(record.value)                
            else:              
                self.object_map[record.level-1].type = None
            self.object_map[record.level-1].add_note(Note(text=Translater.clean_str(record.value)))
        elif isinstance(self.object_map[record.level-1], Fact):
            if not self.object_map[record.level-1].type:
                self.object_map[0].type = FactType.guess(record.value)
        elif record.parent.tag == 'FORM':
            if not self.object_map[0].mediaType:
                self.object_map[0].mediaType = record.value

        else:
            raise ValueError(f"I do not know how to handle 'TYPE' tag for {type(self.object_map[record.level-1])}")

    def handle__url(self, record):
        if isinstance(self.object_map[record.level-2], SourceDescription):
            self.object_map[record.level-2].about = URI.from_url(record.value)
        else:
            raise ValueError(f"Could not handle '_URL' tag in record {record.describe()}, last stack object {self.object_map[record.level-1]}")
            
    def handle_www(self, record):
        if isinstance(self.object_map[record.level-2], SourceReference):
            self.object_map[record.level-2]._description_object.add_identifier(Identifier(value=URI.from_url(record.value)))
        else:
            raise ValueError(f"Could not handle 'WWW' tag in record {record.describe()}, last stack object {self.object_map[record.level-1]}")

