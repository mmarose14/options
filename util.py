import api
from datetime import datetime, timedelta

def gatherOptionData(option):
    option_data = {}

    option_data['symbol'] = option['underlying']
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

    if(isinstance(expirations_list, str)):
        return []

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

def getTimeStamp():
    date_object = datetime.now()

    date_str = datetime.strftime(date_object, "%Y-%m-%d %H:%M:%S")
    return date_str

def optionOutput(option):
    delta = -999
    if ('delta' in option):
        delta = option['delta']

    #Estimated premium (mid price)
    premium = round((option['bid'] + option['ask']) / 2,2)

    option_output = '{}, {}, BID:{}, ASK:{}, {}, {}(D), Premium: {}'\
        .format(
            option['expiration'],
            option['strike'],
            option['bid'],
            option['ask'],
            option['volume'],
            delta,
            premium)
    
    return option_output

def shortCallOptionOutput(option):
    delta = -999
    if ('delta' in option):
        delta = option['delta']

    #Estimated premium (mid price)
    premium = round((option['bid'] + option['ask']) / 2,2)

    option_output = '{}, {} {}, {}(D), Premium: {}'\
        .format(
            option['expiration'],
            option['strike'],
            option['volume'],
            delta,
            premium)
    
    return option_output