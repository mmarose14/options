import files
import spreads

#filename_in = "symbols_spreads.txt"
filename_in = "symbols_test.txt"

#Get list of symbols from text file
listOfSymbols = files.getListOfSymbols(filename_in)

options_data = spreads.findPutSpreads(listOfSymbols)

#filename_out = "output_spreads.txt"

#Export option data into a file
#files.exportToFile(options_data, filename_out, api.isSandbox)
