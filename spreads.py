import files
import api
import util
import panda_files
from datetime import datetime, timedelta

def findPutSpreads(ListOfSymbols):

    #Options criteria
    MIN_VOLUME = 1          
    MAX_BID_ASK_SPREAD = .15
    MAX_STRIKES_WIDTH = 5   
    MAX_DELTA = -.2         
    MIN_PREMIUM = .21

    matching_options = []
    data_frame = []

    for symbol in ListOfSymbols:
        print(f"Processing {symbol}...")

        expirations_list = util.listOfLimitedExpirations(symbol,21,47)

        numOptions = 0
        for expiration in expirations_list:
            #This is temporary... add actual dates later
            if (expiration == "2020-12-08"):
                continue

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
                    and delta >= MAX_DELTA
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

                    if (numOptions == 0):
                        matching_options.append(f"Symbol: {symbol}")
                        numOptions += 1

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
                                        net_credit])


                    #Print the screen when a match is found
                    print(f"Found: {option_output} - ({datetime.now()})")

                    #matching_options.append(option_output)

                if (option['type'] == "put"):
                    prev_option_prem = premium
                    prev_option_strike = option['strike']

    panda_files.exportToFile(data_frame, "output_spreads.csv")

    #print(data_frame)
    return matching_options

