#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import html
import os
from typing import List, Optional

BOM = '\ufeff'

# Add hash table for XREF of Zero Recrods?

nonzero = '[1-9]'
level = f'(?P<level>0|{nonzero}[0-9]*)'
atsign = '@'
underscore = '_'
ucletter = '[A-Z]'
tagchar = f'({ucletter}|[0-9]|{underscore})'
xref = f'{atsign}({tagchar})+{atsign}'
d = '\\ '
stdtag = f'{ucletter}({tagchar})*'
exttag = f'{underscore}({tagchar})+'
tag = f'({stdtag}|{exttag})'
voidptr = '@VOID@'
pointer = f'(?P<pointer>{voidptr}|{xref})'
nonat = '[\t -?A-\\U0010ffff]'
noneol = '[\t -\\U0010ffff]'
linestr = f'(?P<linestr>({nonat}|{atsign}{atsign})({noneol})*)'
lineval = f'({pointer}|{linestr})'
eol = '(\\\r(\\\n)?|\\\n)'
line = f'{level}{d}((?P<xref>{xref}){d})?(?P<tag>{tag})({d}{lineval})?{eol}'

class GedcomRecord():
    def __init__(self,line_num=None,level=-1, tag='NONR', xref='', value=None) -> None:
        self.line_num = line_num
        self._subRecords = []
        self.level = int(level)
        self.xref = xref
        self.pointer: bool = False
        self.tag = str(tag).strip()
        self.value = value
        
        self.parent = None
        self.root = None

        if self.value.endswith('@') and self.value.startswith('@'):
            self.xref = self.value.replace('@','')
            if level > 0:
                self.pointer = True

    @property
    def _as_dict_(self):
        record_dict = {
            'level':self.level,
            'xref':self.xref,
            'tag': self.tag,
            'pointer': self.pointer,
            'value': self.value,
            'subrecords': [subrecord._as_dict_ for subrecord in self._subRecords]
        }   
        return record_dict  
    
    def addSubRecord(self, record):
        if record and record.level == self.level+1:
            record.parent = self
            self._subRecords.append(record)
        else:
            raise ValueError(f"SubRecord must be next level from this record (level:{self.level}, subRecord has level {record.level})")
    
    def recordOnly(self):
        return GedcomRecord(line_num=self.line_num,level=self.level,tag=self.tag,value=self.value)

    def dump(self):
        record_dump = f"Level: {self.level}, tag: {self.tag}, value: {self.value}, subRecords: {len(self._subRecords)}\n"
        for record in self._subRecords:
            record_dump += "\t" + record.dump()  # Recursively call dump on sub_records and concatenate
        return record_dump
    
    def describe(self,subRecords: bool = False):
        description = f"Line {self.line_num}: {'\t'* self.level} Level: {self.level}, tag: '{self.tag}', value: '{self.value}', subRecords: {len(self._subRecords)}"
        if subRecords:
            for subRecord in self.subRecords():
                description = description + '\n' + subRecord.describe(subRecords=True)
        return description

    
    def subRecord(self, tag):
        result = [record for record in self._subRecords if record.tag == tag]
        if len(result) == 0: return None
        return result

    def subRecords(self, tag: str = None):
        if not tag:
            return self._subRecords
        else:
            tags = tag.split("/", 1)  # Split into first tag and the rest

            # Collect all records matching the first tag
            matching_records = [record for record in self._subRecords if record.tag == tags[0]]

            if not matching_records:
                return None  # No matching records found for the first tag

            if len(tags) == 1:
                return matching_records  # Return all matching records for the final tag

            # Recurse into each matching record's subRecords and collect results
            results = []
            for record in matching_records:
                sub_result = record.subRecords(tags[1])
                if sub_result:
                    if isinstance(sub_result, list):
                        results.extend(sub_result)
                    else:
                        results.append(sub_result)

            return results if results else None
    
    def __call__(self) -> None:
        return self.describe()
    
    def __iter__(self):
        return self._flatten_subrecords(self)

    def _flatten_subrecords(self, record):
        yield record
        for subrecord in record._subRecords:
            yield from self._flatten_subrecords(subrecord)

class Gedcom():
    top_level_tags = ['INDI', 'FAM', 'OBJE', 'SOUR', 'REPO', 'NOTE', 'HEAD']

    # =========================================================
    # 1. INITIALIZATION
    # =========================================================
    

    def __init__(self, records: Optional[List[GedcomRecord]] = None,filepath: str = None) -> None:
        if filepath:
            self.records = self._records_from_file(filepath)
        elif records:
            self.records: List[GedcomRecord] = records if records else []
        
        
        self._sources = []
        self._repositories = []
        self._individuals = []
        self._families = []
        self._objects = []

        if self.records:
            for record in self.records:
                if record.tag == 'INDI':
                    record.xref = record.value
                    self._individuals.append(record)
                if record.tag == 'SOUR' and record.level == 0:
                    record.xref = record.value
                    self._sources.append(record)
                if record.tag == 'REPO' and record.level == 0:
                    record.xref = record.value
                    self._repositories.append(record)
                if record.tag == 'FAM' and record.level == 0:
                    record.xref = record.value
                    self._families.append(record)
                if record.tag == 'OBJE' and record.level == 0:
                    record.xref = record.value
                    self._objects.append(record)

    # =========================================================
    # 2. PROPERTY ACCESSORS (GETTERS & SETTERS)
    # =========================================================

    @property
    def json(self):
        import json
        return json.dumps({'Individuals': [indi._as_dict_ for indi in self._individuals]},indent=4)

    def stats(self):
        def print_table(pairs):

            # Calculate the width of the columns
            name_width = max(len(name) for name, _ in pairs)
            value_width = max(len(str(value)) for _, value in pairs)

            # Print the header
            print('GEDCOM Import Results')
            header = f"{'Type'.ljust(name_width)} | {'Count'.ljust(value_width)}"
            print('-' * len(header))
            print(header)
            print('-' * len(header))

            # Print each pair in the table
            for name, value in pairs:
                print(f"{name.ljust(name_width)} | {str(value).ljust(value_width)}")
                
        imports_stats = [
            ('Top Level Records', len(self.records)),
            ('Individuals', len(self.individuals)),
            ('Family Group Records', len(self.families)),
            ('Repositories', len(self.repositories)),
            ('Sources', len(self.sources)),
            ('Objects', len(self.objects))
        ]

        print_table(imports_stats)

    @property
    def sources(self) -> List[GedcomRecord]:
        return self._sources

    @sources.setter
    def sources(self, value: List[GedcomRecord]):
        if not isinstance(value, list) or not all(isinstance(item, GedcomRecord) for item in value):
            raise ValueError("sources must be a list of GedcomRecord objects.")
        self._sources = value

    @property
    def repositories(self) -> List[GedcomRecord]:
        return self._repositories

    @repositories.setter
    def repositories(self, value: List[GedcomRecord]):
        if not isinstance(value, list) or not all(isinstance(item, GedcomRecord) for item in value):
            raise ValueError("repositories must be a list of GedcomRecord objects.")
        self._repositories = value

    @property
    def individuals(self) -> List[GedcomRecord]:
        return self._individuals

    @individuals.setter
    def individuals(self, value: List[GedcomRecord]):
        if not isinstance(value, list) or not all(isinstance(item, GedcomRecord) for item in value):
            raise ValueError("individuals must be a list of GedcomRecord objects.")
        self._individuals = value

    @property
    def families(self) -> List[GedcomRecord]:
        return self._families

    @families.setter
    def families(self, value: List[GedcomRecord]):
        if not isinstance(value, list) or not all(isinstance(item, GedcomRecord) for item in value):
            raise ValueError("families must be a list of GedcomRecord objects.")
        self._families = value

    @property
    def objects(self) -> List[GedcomRecord]:
        return self._objects

    @objects.setter
    def objects(self, value: List[GedcomRecord]):
        if not isinstance(value, list) or not all(isinstance(item, GedcomRecord) for item in value):
            raise ValueError("objects must be a list of GedcomRecord objects.")
        self._objects = value

    # =========================================================
    # 3. METHODS
    # =========================================================

    def write(self):
        """
        Method placeholder for writing GEDCOM files.
        """
        raise NotImplementedError("Writing of GEDCOM files is not implemented.")  

    @staticmethod
    def _records_from_file(filepath: str) -> List[GedcomRecord]:
        extension = '.ged'

        if not os.path.exists(filepath):
            print(f"File does not exist: {filepath}")
            raise FileNotFoundError
        elif not filepath.lower().endswith(extension.lower()):
            print(f"File does not have the correct extension: {filepath}")
            raise Exception("File does not appear to be a GEDCOM")
        
        print("Reading from GEDCOM file")
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file]

            records = []
            record_map = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None}
            for l, line in enumerate(lines):
                if line.startswith(BOM):
                    line = line.lstrip(BOM)
                line = html.unescape(line).replace('&quot;', '')

                if line.strip() == '':
                    continue

                level, tag, value = '', '', ''

                # Split the line into the first two columns and the rest
                parts = line.split(maxsplit=2)
                if len(parts) == 3:
                    level, col2, col3 = parts

                    if col3 in Gedcom.top_level_tags:
                        tag = col3
                        value = col2
                    else:
                        tag = col2
                        value = col3
                else:
                    level, tag = parts

                level = int(level)

                new_record = GedcomRecord(line_num=l + 1, level=level, tag=tag, value=value)
                if level == 0:
                    records.append(new_record)
                else:
                    new_record.root = record_map[0]
                    new_record.parent = record_map[int(level) - 1]
                    record_map[int(level) - 1].addSubRecord(new_record)
                record_map[int(level)] = new_record
        
        return records if records else None

    @staticmethod
    def fromFile(filepath: str) -> 'Gedcom':
        """
        Static method to create a Gedcom object from a GEDCOM file.

        Args:
            filepath (str): The path to the GEDCOM file.

        Returns:
            Gedcom: An instance of the Gedcom class.
        """     
        records = Gedcom._records_from_file(filepath)
        gedcom = Gedcom(records=records)      

        return gedcom

#
#import re
#filepath = r"C:\Users\User\Documents\PythonProjects\gedcomx\.ged_files\_DJC_ Nunda Cartwright Family.ged"
#with open(filepath, 'r', encoding='utf-8') as file:
#    string = file.read()
#
#for match in re.finditer(line, string):
#    data = match.groupdict()
#    print(data)
#'''