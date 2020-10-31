import api
from datetime import datetime, timedelta

MIN_DTE = 20                        #Minimum DTE
MAX_DTE = 50                        #Maximum DTE

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

def listOfAllExpirations(symbol):
    #Get option expirations for symbol
    expirations_list = api.getOptionExpirations(symbol)

    expirations = []

    for expiration_date in expirations_list:
        expirations.append(expiration_date)

    return expirations


def listOfLimitedExpirations(symbol, min_dte, max_dte):
    #Get option expirations for symbol
    expirations_list = api.getOptionExpirations(symbol)

    expirations = []

    for expiration_date in expirations_list:
        #Extract dates within set DTE
        date_object = datetime.strptime(expiration_date,"%Y-%m-%d")
        expiration_min_date = datetime.now() + timedelta(min_dte)
        expiration_max_date = datetime.now() + timedelta(max_dte)

        if (date_object <= expiration_min_date):
            continue

        if (date_object >= expiration_max_date):
            break

        expirations.append(expiration_date)

    return expirations