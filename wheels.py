import api
import files
import util
import panda_files

def findWheels(ListOfSymbols):
    #filename_out = "output_{}.txt".format(config.STRATEGY)

    MAX_BID_ASK_SPREAD = .10
    MIN_PRICE = 10
    MAX_PRICE = 20
    MIN_PREM = .2
    MAX_DELTA = -.16

    matching_options = []
    data_frame = []
    for symbol in ListOfSymbols:
        print(f"Processing {symbol}...")

        last_price = api.getLastStockPrice(symbol)
        if (last_price <= MIN_PRICE or last_price >= MAX_PRICE):
            continue

        expirations_list = util.listOfLimitedExpirations(symbol,30,45)

        numOptions = 0
        for expiration in expirations_list:
            options = api.getOptionsChain(symbol, expiration)

            for option_item in options:
                option = util.gatherOptionData(option_item)

                if (option['bid'] is None):
                    continue

                #Estimated premium (mid price)
                premium = round((option['bid'] + option['ask']) / 2,2)

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
                            option['delta'],
                            premium)

                    if (numOptions == 0):
                        matching_options.append(f"Symbol: {symbol}")
                        numOptions += 1
                    
                    #matching_options.append(f"Wheel: {option_output} - ({datetime.now()})")
                    #line = f"Wheel: {symbol} {option_output} - ({datetime.now()})"
                    #files.appendLineToFile(line, filename_out)

                    #Print the screen when a match is found
                    print(f"Wheel: {option_output} - ({datetime.now()})")

                    data_frame.append([symbol,
                                        option['expiration'],
                                        option['strike'],
                                        option['bid'],
                                        option['ask'],
                                        option['volume'],
                                        delta,
                                        premium,
                                        ""])
    panda_files.exportToFile(data_frame, "output_wheels.csv")
    return ""