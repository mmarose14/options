import api
import files
from datetime import datetime, timedelta

#Options criteria
VOL_THRESHOLD = 1           #Adjust for liquidity
MAX_BID_ASK_SPREAD = .1     #Adjust for liquidity
MAX_STRIKES_WIDTH = 1       #Minimize vertical spread loss
MAX_DELTA = -.16            #Delta threshold
MIN_DTE = 0                 #Minimum DTE
MAX_DTE = 60                #Maximum DTE
MIN_PREMIUM = .15           #Minimum credit received

def processOptionData(option):
    #Gather option data
    option_exp = option['expiration_date']
    option_type = option['option_type']
    option_strike = option['strike']
    option_bid = option['bid']
    option_ask = option['ask']
    option_vol = option['volume']

    #Add necessary greeks here plus rounding
    option_greeks = option.get('greeks',None)
    option_delta = 0
    if (option_greeks):
        option_delta = round(option_greeks['delta'],2)

    #Estimated premium (mid price)
    premium = round( (option_bid + option_ask) / 2, 2)

    #Format the output
    #Filter out options based on criteria set at the top of this file, plus a few others
    if (option_type == "put"
        and option_bid > 0.0
        and premium >= MIN_PREMIUM
        and option_delta >= MAX_DELTA
        and (option_ask - option_bid) <= MAX_BID_ASK_SPREAD
        and option['volume'] > VOL_THRESHOLD):

        option_output = '{}, {}, BID:{}, ASK:{}, {}, {}(D), Premium: {}'\
            .format(option_exp, option_strike,option_bid,option_ask,option_vol,option_delta,premium)

        return option_output

def processSymbols(ListOfSymbols):
    expirations = []

    for symbol in ListOfSymbols:
        #expirations.append(f"Symbol: {symbol}")

        print(f"Processing {symbol}...")

        #Endpoint for options expirations
        expirations_data = api.getOptionExpirations(symbol)

        if (expirations_data['expirations'] is None):
            continue

        list = expirations_data['expirations']['date']

        numOptions = 0
        for expiration_date in list:
            #Extract dates within set DTE
            date_object = datetime.strptime(expiration_date,"%Y-%m-%d")
            expiration_min_days = datetime.now() + timedelta(MIN_DTE)
            expiration_max_days = datetime.now() + timedelta(MAX_DTE)

            #Find expirations only within the specified DTE criteria
            #if (expiration_min_days <= date_object <= expiration_max_days): #(There's a bug here)
            if (date_object <= expiration_max_days):

                #Now get the options chain for the expiration
                #Data is only updated on the server once per hour on the hour
                options_chain = api.getOptionsChain(symbol,expiration_date)
                list_of_options = options_chain['options']['option']

                prev_option_strike = 0
                prev_option_prem = 0
                for option in list_of_options:
                    #Get the estimated premium for use later
                    premium = round( (option['bid'] + option['ask']) / 2, 2)

                    #Check option for specific criteria and then format it for output
                    option_output = processOptionData(option)
                    if (option_output):
                        if (numOptions == 0):
                            expirations.append(f"Symbol: {symbol}")
                            numOptions += 1
                        
                        #Figure out net credit from credit spread
                        net_credit = round ((premium - prev_option_prem),2)

                        if (net_credit >= MIN_PREMIUM):
                            #Mark a strike where the width between the current strike and the previous strike meets the criteria
                            if (option['strike'] - prev_option_strike == MAX_STRIKES_WIDTH):
                                option_output = option_output + " <<<<<< "
                                option_output = option_output + f"{net_credit}"

                            expirations.append(option_output)
                        
                        prev_option_strike = option['strike']
                    
                    if (option['option_type'] == "put"):
                        prev_option_prem = premium
            else:
                break   #No need to parse future dates

    return expirations




          

