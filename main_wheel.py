import files
import wheels

#Get list of symbols from text file
filename_in = "symbols_wheels.txt"

listOfSymbols = files.getListOfSymbols(filename_in)

#Find wheel options
wheels.findWheels(listOfSymbols)
