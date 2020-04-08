import os

TEST_ONLY = False   #Only used for list of test symbols (symbols-test.txt)

def getListOfSymbols():
    #Current directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    if (TEST_ONLY):
        filename = "symbols-test.txt"
    else:
        filename = "symbols.txt"

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

def exportToFile(expirations,sandbox):
    if (sandbox):
        filename = "output.txt"
    else:
        filename = "output-prod.txt"

    output_file = open(filename, "w+")

    for line in expirations:
            output_file.writelines(f"{line}\n")