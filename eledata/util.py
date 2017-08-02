import csv
import codecs
import os
import xlrd
import datetime
import distutils.core

from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

def parser_to_list_of_dictionaries(parser, headerRow=None, numLines=float("inf"), list=None):
    """
    Takes a csv file stores its contents into the given list, replacing the old
    content, or creating a new list if no list is given. The csv file is
    expected to be stored in the format:
    
    <header line optional> header 1,header 2,header 3, . . .
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
    
    If headerRow is None, it auto generates a header row in the format 
    ["column 1", "column 2", ...]
    """
    
    list = [] if list is None else list
    del list[:]
    
    first = True
    for row in parser:
        # numLines can be thought of as the number of lines remaining to be
        # parsed
        if numLines <= 0:
            return list
        numLines -= 1
        
        if headerRow is None:
            headerRow = ["column %s" % (i+1) for i in range(len(row))]
            
        if len(row) != len(headerRow):
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
            dataPointDict[to_string(headerRow[i])] = to_string(row[i])
        
        list += (dataPointDict,)
            
    return list



def file_to_list_of_dictionaries(file, numLines=float("inf"), list=None, is_header_included=True):
    parser = None
    _, extension = os.path.splitext(file.name)
    
    if extension.lower() in [".csv", ".tsv"]:
        # Reading the dialect from the file.
        dialect = csv.Sniffer().sniff(
                codecs.EncodedFile(file, "utf-8").read(1024), delimiters=",\t")
        
        file.seek(0) # reset the read point
        
        def csv_generator(csv_reader):
            for line in csv_reader:
                yield line
        
        parser = csv_generator(csv.reader(codecs.EncodedFile(file, "utf-8"),
            dialect=dialect))
        
    elif extension.lower() in [".xls",".xlsx"]:
        def xl_generator(worksheet):
            for i in range(worksheet.nrows):
                yield ws.row(i)
            
        ws = xlrd.open_workbook(file.name).sheet_by_index(0)
        parser = xl_generator(ws)
    else:
        raise InvalidInputError("Unknown filetype: " + file.name)
        
    if is_header_included:
        headerRow = next(parser)
    else:
        headerRow = None
    
    return parser_to_list_of_dictionaries(parser, headerRow=headerRow, numLines=numLines, list=list)
    


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
        "number":float,
        "bool":lambda str: bool(distutils.util.strtobool(str)),
    }


def to_json(data):
    return JSONRenderer().render(data)
    
def from_json(json_string):
    ret = JSONParser().parse(BytesIO(str(json_string)))
    return ret


def debug_deep_compare(param1, param2):
    if dir(param1) != dir(param2):
        print "The two objects have different parameters"
    for field in dir(param1):
        if hasattr(param1, field) and hasattr(param2, field):
            if getattr(param1, field) != getattr(param2, field):
                print "obj1.%s: %s,    obj2.%s: %s" % (field, getattr(param1, field), field, getattr(param2, field))
        elif hasattr(param1, field) != hasattr(param2, field):
            print "Two objects differ by field: %s. One object is missing the field." % field

# Infinite recursion warning: reference loops are possible and not checked for
# in this function. Use only for debugging.
def debug_deep_print(obj):
    print type(obj), ": {"
    for field in dir(obj):
        try:
            print field, ": ", getattr(obj, field), ", "
        except Exception:
            print "Got error when trying to read field '", field, "',"
    print "}"
