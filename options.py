import api
import files
from datetime import datetime, timedelta

#Options criteria
MIN_VOLUME = 100                    #Adjust for liquidity
MAX_BID_ASK_SPREAD = .10            #Adjust for liquidity
MIN_OPEN_INT = 1                    #Minimum open interest
MAX_STRIKES_WIDTH = 5               #Minimize vertical spread loss
MAX_DELTA = -.16                    #Delta threshold (short)
MIN_DELTA = .1                      #Delta threshold (long) - Abs
MAX_THETA = -.1                     #Theta threshold (long)
MIN_DTE = 10                        #Minimum DTE
MAX_DTE = 45                        #Maximum DTE
MIN_PREMIUM = .10                   #Minimum credit received
MAX_OPTION_ASK = .03                #For buying options

def listOfExpirations(symbol):
    #Get option expirations for symbol
    expirations_list = api.getOptionExpirations(symbol)

    expirations = []

    for expiration_date in expirations_list:
        #Extract dates within set DTE
        date_object = datetime.strptime(expiration_date,"%Y-%m-%d")
        expiration_min_date = datetime.now() + timedelta(MIN_DTE)
        expiration_max_date = datetime.now() + timedelta(MAX_DTE)

        if (date_object <= expiration_min_date):
            continue

        if (date_object >= expiration_max_date):
            break

        expirations.append(expiration_date)

    return expirations

def gatherOptionData(option):
    option_data = {}

    option_data['type'] = option['option_type']
    option_data['expiration'] = option['expiration_date']
    option_data['strike'] = option['strike']
    option_data['bid'] = option['bid']
    option_data['ask'] = option['ask']
    option_data['volume'] = option['volume']
    option_data['open_int'] = option['open_interest']

    #Add necessary greeks here plus rounding
    option_greeks = option.get('greeks',None)

    if (option_greeks):
        option_data['delta'] = option_greeks['delta']
        option_data['theta'] = option_greeks['theta']
        option_data['gamma'] = option_greeks['gamma']

    return option_data

def findPutSpreads(ListOfSymbols):
    matching_options = []

    for symbol in ListOfSymbols:
        print(f"Processing {symbol}...")

        expirations_list = listOfExpirations(symbol)

        numOptions = 0
        for expiration in expirations_list:

            options = api.getOptionsChain(symbol, expiration)

            prev_option_strike = 0
            prev_option_prem = 0
            for option_item in options:
                option = gatherOptionData(option_item)

                if (option['bid'] is None):
                    continue

                #Estimated premium (mid price)
                premium = round((option['bid'] + option['ask']) / 2,2)

                #Figure out net credit from credit spread
                net_credit = round ((premium - prev_option_prem),2)

                #Criteria here
                if (option['type'] == "put"
                    and option['bid'] > 0.0
                    #and premium >= MIN_PREMIUM
                    #and option['delta'] >= MAX_DELTA
                    #and (option['ask'] - option['bid']) <= MAX_BID_ASK_SPREAD
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
                    print(f"Found: {option_output}")

                    matching_options.append(option_output)

                if (option['type'] == "put"):
                    prev_option_prem = premium
                    prev_option_strike = option['strike']
            
    return matching_options

#Rewrite this
def scanForCheapOptions(ListOfSymbols):
    expirations = []

    for symbol in ListOfSymbols:
        print(f"Processing {symbol}...")

        last_price = api.getLastStockPrice(symbol)

        #Endpoint for options expirations
        expirations_data = api.getOptionExpirations(symbol)

        if (expirations_data['expirations'] is None):
            continue

        list = expirations_data['expirations']['date']

        numOptions = 0
        for expiration_date in list:
            date_object = datetime.strptime(expiration_date,"%Y-%m-%d")
            expiration_min_date = datetime.now() + timedelta(MIN_DTE)

            if (date_object <= expiration_min_date):
                continue

            #Now get the options chain for the expiration
            options_chain = api.getOptionsChain(symbol,expiration_date)
            list_of_options = options_chain['options']['option']

            for option in list_of_options:
                #Gather option data
                option_type = option['option_type']
                option_exp = option['expiration_date']
                option_strike = option['strike']
                option_bid = option['bid']
                option_ask = option['ask']
                #option_vol = option['volume']
                option_int = option['open_interest']

                #Add necessary greeks here plus rounding
                option_greeks = option.get('greeks',None)
                option_delta = 0
                if (option_greeks):
                    option_delta = abs(option_greeks['delta'])
                    option_theta = 100 * round(option_greeks['theta'],5)
                    option_gamma = round(option_greeks['gamma'],5)

                #Estimated premium (mid price)
                premium = round( (option_bid + option_ask) / 2, 2)

                #Filter criteria here
                option_output = None
                if (0.0 < option_ask <= MAX_OPTION_ASK
                    and option_int >= MIN_OPEN_INT
                    and option_delta >= MIN_DELTA
                    ):

                    option_output = '{} {}, {}, BID:{}, ASK:{}, {}, {}(D), {}(G), Premium: {}, {}(T)' \
                        .format(option_type,
                                option_exp,
                                option_strike,
                                option_bid,
                                option_ask,
                                option_int,
                                option_delta,
                                option_gamma,
                                premium,
                                option_theta, 
                                )

                    #Print the screen when a match is found
                    print(f"Found: {option_output}")

                if (option_output):
                    if (numOptions == 0):
                        expirations.append(f"Symbol: {symbol} Last: {last_price}")
                        numOptions += 1

                    expirations.append(option_output)

    return expirations

def findDeltaHedges(ListOfSymbols):
    
    matching_options = []
    for symbol in ListOfSymbols:
        expirations_list = listOfExpirations(symbol)

        numOptions = 0
        for expiration in expirations_list:
            options = api.getOptionsChain(symbol, expiration)

            for option_item in options:

                option = gatherOptionData(option_item)

                #Estimated premium (mid price)
                premium = round((option['bid'] + option['ask']) / 2,2)

                if (
                    abs(option['delta']) >= .04
                    and option['open_int'] >= 1
                    and premium <= 1
                    #and option['theta'] >= -.11
                    ):

                    if (numOptions == 0):
                        matching_options.append(f"Symbol: {symbol}")
                        numOptions += 1
                    
                    option_output = '{} {}, {}, BID:{}, ASK:{}, {}, {}(D), {}(G), Premium: {}, {}(T)' \
                            .format(option['type'],
                                    option['expiration'],
                                    option['strike'],
                                    option['bid'],
                                    option['ask'],
                                    option['open_int'],
                                    option['delta'],
                                    option['gamma'],
                                    premium,
                                    option['theta'], 
                                    )
                        
                    #Print the screen when a match is found
                    print(f"Found: {option_output}")

                    matching_options.append(option_output)
    
    return matching_options
          
def findCoveredCalls(ListOfSymbols):
    matching_options = []

    for symbol in ListOfSymbols:
        last_price = api.getLastStockPrice(symbol)

        expirations_list = listOfExpirations(symbol)

        numOptions = 0
        for expiration in expirations_list:
            options = api.getOptionsChain(symbol, expiration)

            for option_item in options:
                option = gatherOptionData(option_item)

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
