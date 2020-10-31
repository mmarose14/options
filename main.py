import files
import options
import api

filename = "symbols_spreads.txt"

#Get list of symbols from text file
listOfSymbols = files.getListOfSymbols(filename)

#Choose strategy
options_data = options.findPutSpreads(listOfSymbols)
#options_data = options.findCoveredCalls(listOfSymbols)

#options.findCheapPuts(listOfSymbols)
#options_data = options.findWheels(listOfSymbols)

#Export option data into a file
files.exportToFile(options_data, filename, api.isSandbox)
