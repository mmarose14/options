import os

def getListOfSymbols(filename):
    #Current directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    #Read ticker symbols file - default file contains options with high IV
    symbols = open("symbols/" + filename,"r")
    symbols.close

    #Strip newline and create object
    ListOfSymbols = [line.strip() for line in symbols]

    #Remove symbols from ignore list
    ListOfSymbols = [item for item in ListOfSymbols]

    return ListOfSymbols

def exportToFile(expirations,filename,sandbox):
    output_file = open("output/" + filename, "w+")

    for line in expirations:
        if ("<" in line or "Symbol" in line or "Wheel" in line):
            str_output = line + "\n"
            output_file.write(str_output)

def appendLineToFile(line,filename):
    output_file = open("output/" + filename, "a+")

    str_output = line + "\n"
    output_file.write(str_output)
    output_file.close