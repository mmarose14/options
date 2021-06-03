import config
import api
import util
import panda_files
from datetime import datetime

def main():
    #Get list of symbols from file
    filename_in = "champions.csv"

    listOfSymbols = panda_files.importCSV(filename_in)

    #Find wheel options
    findWheels(listOfSymbols, 10, 47)

def findWheels(ListOfSymbols, minDays, maxDays):

    MAX_BID_ASK_SPREAD = .15
    MIN_PRICE = 10
    MAX_PRICE = 70
    MIN_PREM = .30
    MAX_DELTA = -.2

    matching_options = []
    data_frame = []
    for symbol in ListOfSymbols:
        print(f"Processing {symbol}...")

        last_price = api.getLastStockPrice(symbol)
        if (last_price <= MIN_PRICE or last_price >= MAX_PRICE):
            continue

        expirations_list = util.listOfLimitedExpirations(symbol, minDays, maxDays)

        numOptions = 0
        for expiration in expirations_list:
            options = api.getOptionsChain(symbol, expiration)

            for option_item in options:
                option = util.gatherOptionData(option_item)

                if (option['bid'] is None or option['ask'] is None):
                    continue

                #Estimated premium (mid price)
                premium = round((option['bid'] + option['ask']) / 2,2)

                delta = -999
                if ('delta' in option):
                    delta = option['delta']

                if (option['type'] == "put"
                    and option['bid'] > 0
                    and delta >= MAX_DELTA
                    and premium >= MIN_PREM
                    and (option['ask'] - option['bid']) <= MAX_BID_ASK_SPREAD
                    and option['volume'] > 0
                ):
                    option_output = '{}, {}, BID:{}, ASK:{}, {}, {}(D), Premium: {}'\
                        .format(
                            option['expiration'],
                            option['strike'],
                            option['bid'],
                            option['ask'],
                            option['volume'],
                            delta,
                            premium)

                    if (numOptions == 0):
                        matching_options.append(f"Symbol: {symbol}")
                        numOptions += 1

                    #Print the screen when a match is found
                    print(f"Wheel: {option_output} - ({util.getTimeStamp()})")

                    data_frame.append([symbol,
                                        option['expiration'],
                                        option['strike'],
                                        option['bid'],
                                        option['ask'],
                                        option['volume'],
                                        delta,
                                        premium,
                                        "",
                                        util.getTimeStamp()])

    panda_files.exportToFile(data_frame, "output_wheels.csv")
    
    if (config.REMOTE):
        panda_files.exportToWeb(data_frame, "output_wheels")
        panda_files.exportToJson(data_frame, "output_wheels")

    return ""

if __name__ == '__main__':
    main()