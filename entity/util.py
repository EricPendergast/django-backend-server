import csv
def csv_to_list_of_dictionaries(file, numLines=float("inf"), list=None):
    """
    Takes a csv file stores its contents into the given list, creating a new one if no list is given. The csv file is expected to be stored in the format:
    
    header 1,header 2,header 3, . . .
    11,12,13
    21,22,23
    31,32,33
    .       .
    .        .
    .         .
    
    The list returned will be in the format:
    
    [{header1:11,header2:12,header3:13, ...},
     {header1:21,header2:22,header3:33, ...},
     .
     .
     .
    ]
    """
    # assert request.list["file_format"] == "csv",\
    # "TODO: allow use of tsv file format"
    
    list = [] if list is None else list
    reader = csv.reader(file)
    
    firstRow = None
    rowCount = 0
    for row in reader:
        if numLines <= 0:
            return list
        numLines -= 1
        
        if firstRow is None:
            firstRow = row
            numLines += 1
        else:
            assert len(row) == len(firstRow),\
            "Header row and subsequent row(s) are not the same length"
                
            # each item in the list list is refered to as a "data
            # point"
            dataPointDict = {}
            for i in range(0, len(row)):
                dataPointDict[firstRow[i]] = row[i]
            
            list += (dataPointDict,)
            
            
    return list
