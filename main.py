import files
import options
import api

#Get list of symbols from text file
listOfSymbols = files.getListOfSymbols()

#Choose strategy
#options_data = options.findDeltaHedges(listOfSymbols)
#options_data = options.scanForCheapOptions(listOfSymbols)
#options_data = options.findPutSpreads(listOfSymbols)
options_data = options.findCoveredCalls(listOfSymbols)

#Export option data into a file
files.exportToFile(options_data, api.isSandbox)
