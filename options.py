import api
import files
import util
from datetime import datetime, timedelta

#Options criteria
MIN_VOLUME = 1                    #Adjust for liquidity
MAX_BID_ASK_SPREAD = .10            #Adjust for liquidity
MIN_OPEN_INT = 1                    #Minimum open interest
MAX_STRIKES_WIDTH = 5               #Minimize vertical spread loss
MAX_DELTA = -.11                    #Delta threshold (short)
MIN_DELTA = .1                      #Delta threshold (long) - Abs
MAX_THETA = -.1                     #Theta threshold (long)
MIN_PREMIUM = .21                   #Minimum credit received
MAX_OPTION_ASK = .03                #For buying options

def message(str):
    print(str)

def findPutSpreads(ListOfSymbols):
    matching_options = []

    for symbol in ListOfSymbols:
        print(f"Processing {symbol}...")

        expirations_list = util.listOfLimitedExpirations(symbol,20,50)

        numOptions = 0
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
                            option['delta'],
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


                    #Print the screen when a match is found
                    print(f"Found: {option_output} - ({datetime.now()})")

                    matching_options.append(option_output)

                if (option['type'] == "put"):
                    prev_option_prem = premium
                    prev_option_strike = option['strike']

    return matching_options

def findCoveredCalls(ListOfSymbols):
    matching_options = []

    for symbol in ListOfSymbols:
        last_price = api.getLastStockPrice(symbol)

        expirations_list = util.listOfLimitedExpirations(symbol,20,50)

        numOptions = 0
        for expiration in expirations_list:
            options = api.getOptionsChain(symbol, expiration)

            for option_item in options:
                option = util.gatherOptionData(option_item)

                if (option['strike'] <= last_price):
                    continue

                premium = round((option['bid'] + option['ask']) / 2,2)
                profit = round(100 * ((option['strike'] - last_price) + premium))
                debit = round ( (100 * last_price) - (100 * premium) )

                if (option['bid'] > 0
                    and debit <= 1000
                    and option['type'] == "call"
                    and last_price <= 15
                    and option['volume'] > 0):

                    if (numOptions == 0):
                        matching_options.append(f"Symbol: {symbol}, Last: {last_price}")
                        numOptions += 1

                    option_output = '{} {}, {}, BID:{}, ASK:{}, {}, {}(D), Premium: {}, Debit: {}, Profit: {}' \
                        .format(option['type'],
                                option['expiration'],
                                option['strike'],
                                option['bid'],
                                option['ask'],
                                option['open_int'],
                                option['delta'],
                                premium,
                                debit,
                                profit
                                )

                    #Print the screen when a match is found
                    print(f"Found: {option_output}")

                    matching_options.append(option_output)


    return matching_options

def findHigherRiskCreditSpreads(ListOfSymbols):

    for symbol in ListOfSymbols:
        expirations_list = util.listOfLimitedExpirations(symbol,0,90)

        for expiration in expirations_list:
            options = api.getOptionsChain(symbol, expiration)

            cheapest_option = 0
            highest_premium = 0
            for option_item in options:
                option = util.gatherOptionData(option_item)

                #Estimated premium (mid price)
                premium = round((option['bid'] + option['ask']) / 2,2)

                if ('delta' in option):
                    delta = option['delta']

                #Criteria
                if (option['type'] == "put"
                    and option['open_int'] > 0
                    and option['bid'] > 0.0
                ):
                    
                    if (cheapest_option == 0):
                        cheapest_option = option
                        cheapest_option['premium'] = premium
                
                if (option['type'] == "put"
                    and option['bid'] > 0.0
                    and option['volume'] > MIN_VOLUME
                    and delta >= -.16 
                ):

                    highest_premium = option
                    highest_premium['premium']  = premium

            if (cheapest_option == 0):
                continue

            if (highest_premium == 0):
                continue

            ### OUTPUT
            high_spread = highest_premium['ask'] - highest_premium['bid']
            net = round(highest_premium['premium'] - cheapest_option['premium'],2)
            max_loss = ((highest_premium['strike'] - cheapest_option['strike']) - net)
            if (max_loss > 0 and net > 0):
                risk = round(max_loss / net, 2)

            #Only print the options worth our while
            if (net >= .3
                and max_loss <= 8
                and high_spread <= .15
            ):

                #Print LONG option
                output = 'Buy: {}, {}, {}'\
                            .format(
                                cheapest_option['expiration'],
                                cheapest_option['strike'],
                                cheapest_option['premium']
                            )
                print(f"{symbol} {output}")

                #Print SHORT option
                output = 'Sell: {}, {}, {}'\
                            .format(
                                highest_premium['expiration'],
                                highest_premium['strike'],
                                highest_premium['premium']
                            )
                print(f"{symbol} {output}")

                #Print net profit
                print(f"Net: {net}")

                #Print Max loss
                print(f"Max Loss: {max_loss}")
                print(f"Risk: {risk}")
                print("--")

def checkWheelPositions(Positions):
    for position in Positions:

        symbol = position['pos_symbol']
        trade_price = position['pos_trade_price']
        
        options = api.getOptionsChain(symbol,position['pos_expiration'])
        for option_item in options:
            if (option_item['strike'] == position['pos_strike']
                and option_item['option_type'] == position['pos_type']
            ):
                mid = (option_item['ask'] + option_item['bid']) / 2
                gain = round(((trade_price - mid) * 100),2)
                
                print("---")
                print(f"Position {symbol} gain: {gain}")

                post_data = {"value1":symbol, "value2":gain}

                if (gain > 0):
                    profit_target = 40
                    profit = gain / trade_price

                    if (profit >= profit_target):
                        print(f"Profit: {profit}")
                        api.sendPush(post_data)
                
                print("---")
            
def checkSpreads():
    position = {}

    
    position['symbol'] = "BIDU"
    position['option_type'] = "put"
    position['expiration'] = "2020-09-18"
    position['leg1_strike'] = 105
    position['leg1_trade_price'] = -53
    position['leg2_strike'] = 100
    position['leg2_trade_price'] = 30

    """
    position['symbol'] = "DOCU"
    position['option_type'] = "put"
    position['expiration'] = "2020-09-18"
    position['leg1_strike'] = 155
    position['leg1_trade_price'] = -92
    position['leg2_strike'] = 150
    position['leg2_trade_price'] = 64
    """

    symbol = position['symbol']

    leg1_bid = 0
    leg1_ask = 0
    leg2_bid = 0
    leg2_ask = 0

    options = api.getOptionsChain(symbol,position['expiration'])
    for option in options:
        if (option['option_type'] == "put"):
            if (option['strike'] == position['leg1_strike']):
                leg1_bid = option['bid']
                leg1_ask = option['ask']
            
            if (option['strike'] == position['leg2_strike']):
                leg2_bid = option['bid']
                leg2_ask = option['ask']

    short_mid = (leg1_ask + leg1_bid) / 2
    long_mid = (leg2_ask + leg2_bid) / 2

    long_mark = long_mid
    short_mark = (-1 * short_mid)

    mark = (long_mark + short_mark) * 100
    trade_price = position['leg1_trade_price'] + position['leg2_trade_price']

    gain = (-1 * trade_price) - (-1 * mark)
    gain_rounded = round(gain, 2)

    print(f"Symbol: {symbol} gain: {gain_rounded}")

def findWheels(ListOfSymbols):
    matching_options = []
    for symbol in ListOfSymbols:
        print(f"Processing {symbol}...")

        expirations_list = util.listOfLimitedExpirations(symbol,1,15)

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
                    and delta >= -.16
                    and premium >= .19
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

                    #Print the screen when a match is found
                    print(f"Found: {option_output} - ({datetime.now()})")

    return matching_options
                
                


