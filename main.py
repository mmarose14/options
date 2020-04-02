import files
import options
import api

#Get list of symbols from text file
listOfSymbols = files.getListOfSymbols()

#Gather data and process it
options_data = options.processSymbols(listOfSymbols)

#Export option data into a file
files.exportToFile(options_data, api.isSandbox)
