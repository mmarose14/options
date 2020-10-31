import os

TEST_ONLY = False   #Only used for list of test symbols (symbols-test.txt)

def getListOfSymbols(filename):
    #Current directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    if (TEST_ONLY):
        filename = "symbols-test.txt"

    #Read ticker symbols file - default file contains options with high IV
    symbols = open(filename,"r")
    symbols.close

    #Read ignore file for symbols to ignore
    ignore_list = open("ignore.txt","r")
    ignore_list.close

    #Strip newline and create object
    ListOfSymbols = [line.rstrip() for line in symbols]
    IgnoreList = [line.rstrip() for line in ignore_list]

    #Remove symbols from ignore list
    ListOfSymbols = [item for item in ListOfSymbols if item not in IgnoreList]

    return ListOfSymbols

def exportToFile(expirations,filename,sandbox):
    output_file = open(filename, "w+")

    for line in expirations:
        if ("<" in line or "Symbol" in line):
            str_output = line + "\n"
            output_file.write(str_output)