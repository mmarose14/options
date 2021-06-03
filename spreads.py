import config
import api
import util
import panda_files
from datetime import datetime

def main():

    filename_in = "stocks-screener-winners.csv"

    #Get symbols from file
    listOfSymbols = panda_files.importCSV(filename_in)

    findPutSpreads(listOfSymbols)

def findPutSpreads(ListOfSymbols):

    #Options criteria
    MIN_VOLUME = 1          
    MAX_BID_ASK_SPREAD = .15
    MAX_STRIKES_WIDTH = 5   
    DELTA = -.2         
    MIN_PREMIUM = .29

    data_frame = []

    for symbol in ListOfSymbols:
        print(f"Processing {symbol}...")

        expirations_list = util.listOfLimitedExpirations(symbol,21,47)
        #Try hard-coded expirations for faster processing
        #expirations_list = ["2021-02-19"]

        for expiration in expirations_list:

            options = api.getOptionsChain(symbol, expiration)

            prev_option_strike = 0
            prev_option_prem = 0
            for option_item in options:
                #Ignore weeklys?
                if (option_item['expiration_type'] == "weeklys"):
                    break

                option = util.gatherOptionData(option_item)

                if (option['bid'] is None):
                    continue

                #Estimated premium (mid price)
                premium = round((option['bid'] + option['ask']) / 2,2)

                #Figure out net credit from credit spread
                net_credit = round ((premium - prev_option_prem),2)


                if ('delta' in option):
                    delta = option['delta']
                    delta = round(delta, 2)

                #Criteria here
                if (option['type'] == "put"
                    and option['bid'] > 0.0
                    and premium >= MIN_PREMIUM
                    and delta >= DELTA
                    and (option['ask'] - option['bid']) <= MAX_BID_ASK_SPREAD
                    and option['volume'] > MIN_VOLUME
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

                    #Mark a strike where the width between the current strike and the previous strike meets the criteria
                    if (net_credit >= MIN_PREMIUM
                        and prev_option_prem > 0
                        and option['strike'] - prev_option_strike <= MAX_STRIKES_WIDTH
                        ):

                        option_output = option_output + " <<<<<< "
                        option_output = option_output + f"{net_credit}"

                        data_frame.append([symbol,
                                        option['expiration'],
                                        option['strike'],
                                        option['bid'],
                                        option['ask'],
                                        option['volume'],
                                        delta,
                                        premium,
                                        net_credit,
                                        util.getTimeStamp()])


                        #Print the screen when a match is found
                        print(f"Found: {option_output} - ({util.getTimeStamp()})")


                if (option['type'] == "put"):
                    prev_option_prem = premium
                    prev_option_strike = option['strike']

    panda_files.exportToFile(data_frame, "output_spreads.csv")
    if (config.REMOTE):
        panda_files.exportToWeb(data_frame, "output_spreads")
        panda_files.exportToJson(data_frame, "output_spreads")

if __name__ == '__main__':
    main()

