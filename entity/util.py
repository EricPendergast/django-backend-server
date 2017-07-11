import csv
import codecs
import os
import xlrd
import re
import datetime

def parser_to_list_of_dictionaries(parser, numLines=float("inf"), list=None):
    """
    Takes a csv file stores its contents into the given list, replacing the old
    content, or creating a new list if no list is given. The csv file is
    expected to be stored in the format:
    
    <csv header line, optional>
    header 1,header 2,header 3, . . .
    11,12,13
    21,22,23
    31,32,33
    .       .
    .        .
    .         .
    
    The list returned will be in the format:
    
    [{header1:11,header2:12,header3:13, ...},
     {header1:21,header2:22,header3:23, ...},
     .
     .
     .
    ]
    """
    
    list = [] if list is None else list
    del list[:]
    
    firstRow = None
    rowCount = 0
    for row in parser:
        if numLines <= 0:
            return list
        numLines -= 1
        
        if firstRow is None:
            firstRow = row
            numLines += 1
        else:
            # "Header row and subsequent row(s) are not the same length"
            if len(row) != len(firstRow):
                raise InvalidInputError("Header row and subsequent row(s) are not the same length")
                
            def to_string(obj):
                if type(obj) is xlrd.sheet.Cell:
                    return str(obj.value)
                else:
                    return str(obj)
            # Each item in the list is refered to as a "data
            # point"
            dataPointDict = {}
            for i in range(0, len(row)):
                dataPointDict[to_string(firstRow[i])] = to_string(row[i])
            
            list += (dataPointDict,)
            
    return list



def file_to_list_of_dictionaries(file, numLines=float("inf"), list=None):
    parser = None
    _, extension = os.path.splitext(file.name)
    
    if extension.lower() in [".csv", ".tsv"]:
        # Reading the dialect from the file.
        dialect = csv.Sniffer().sniff(
                codecs.EncodedFile(file, "utf-8").read(1024), delimiters=",\t")
        # Since we read some stuff from the file, we must reset the point being
        # read from
        file.seek(0)
        parser = csv.reader(codecs.EncodedFile(file, "utf-8"), dialect=dialect)
        
    elif extension.lower() in [".xls",".xlsx"]:
        ws = xlrd.open_workbook(file.name).sheet_by_index(0)
        parser = [ws.row(i) for i in range(ws.nrows)]
    else:
        raise InvalidInputError("Unknown filetype: " + file.name)
        
    
    return parser_to_list_of_dictionaries(parser, numLines=numLines, list=list)
    


class InvalidInputError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg
    
    
# Takes a string representation of a type and returns a function that casts
# strings to that type
string_caster = {
        "string":str,
        "date":lambda str: datetime.datetime.strptime(str, '%d/%m/%Y'),
        "number":float
    }
