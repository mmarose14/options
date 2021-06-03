import config
import api
import util
import panda_files
from datetime import datetime

MAX_BID_ASK_SPREAD = .15

def main():

    filename_in = "LEAPS.csv"

    #Get symbols from file
    listOfSymbols = panda_files.importCSV(filename_in)

    findPMCC(listOfSymbols)

def findPMCC(ListOfSymbols):

    for symbol in ListOfSymbols:
        print(f"Processing {symbol}...")
        expirations_list = util.listOfLimitedExpirations(symbol, 90, 300)

        long_calls = findLongCall(symbol, expirations_list)

        if (long_calls):
            print(F"Search for short calls...")
        
        for long_call in long_calls:
            findShortCall(long_call)


def findLongCall(symbol, expirations_list):
    long_calls = []

    #Find long call
    for expiration in expirations_list:
        options = api.getOptionsChain(symbol, expiration)

        for option_item in options:
            option = util.gatherOptionData(option_item)

            if (option['bid'] is None or option['ask'] is None):
                continue

            #Estimated premium (mid price)
            premium = round((option['bid'] + option['ask']) / 2,2)
            option['premium'] = premium

            delta = -999
            if ('delta' in option):
                delta = option['delta']

            if (option["type"] == "put"
                or premium >= 5
                or option['volume'] == 0
                or delta < .5
                or (option['ask'] - option['bid']) >= MAX_BID_ASK_SPREAD
                ):
                continue

            #Find Long Call
            if (option["type"] == "call"):
                long_calls.append(option)
    
    return long_calls

def findShortCall(long_call):
    symbol = long_call["symbol"]
    long_strike = long_call["strike"]
    long_exp = long_call["expiration"]
    long_prem = long_call["premium"]
    expirations_list = util.listOfLimitedExpirations(symbol, 7, 60)

    long_delta = long_call["delta"]

    for expiration in expirations_list:

        options = api.getOptionsChain(symbol, expiration)

        for option_item in options:
            if (option_item['expiration_type'] == "weeklys"):
                break

            option = util.gatherOptionData(option_item)

            if (option['bid'] is None or option['ask'] is None):
                continue

            #Estimated premium (mid price)
            premium = round((option['bid'] + option['ask']) / 2,2)

            delta = -999
            if ('delta' in option):
                delta = option['delta']
            
            if (option["type"] == "put"
                    or premium <= .3
                    or option['volume'] == 0
                    or delta > .3
                    or (option['ask'] - option['bid']) >= MAX_BID_ASK_SPREAD
                    ):
                    continue

            if (option["type"] == "call"):

                net_debit = round(long_prem - premium,2)
                width_of_strike = option["strike"] - long_strike

                if (net_debit > 2
                    or (width_of_strike * .75) <= net_debit
                    ):
                    continue

                option_output = util.shortCallOptionOutput(option)
                
                print("---")
                print(f"PMCC - L: {long_strike} | {long_exp} | {long_delta}(D)")
                print(f"PMCC - S: {option_output}")
                print(f"Net Debit: {net_debit} Width: {width_of_strike}")


if __name__ == '__main__':
    main()


