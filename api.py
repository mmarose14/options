# API operations
# Utilizes the Tradier API - https://documentation.tradier.com/brokerage-api

import config
import requests
import json

#Switch environment
ENV = "sandbox"
#ENV = "api"


def isSandbox(): return (ENV == "sandbox")

#Retrieve data from url endpoint
def getAPIData(url):
    bearer_token = f"Bearer {config.API_TOKEN}"
    headers={'Authorization': bearer_token, 'Accept': 'application/json'}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))

def getLastStockPrice(symbol):
    url = f"https://{ENV}.tradier.com/v1/markets/quotes?symbols={symbol}"
    quote_data = getAPIData(url)
    last_price = quote_data['quotes']['quote']['last']
    return last_price

def getOptionExpirations(symbol):
    url = f"https://{ENV}.tradier.com/v1/markets/options/expirations?symbol={symbol}"
    expirations_data = getAPIData(url)
    return expirations_data

def getOptionsChain(symbol, expiration):
    #Endpoint for options chain
    url = f"https://{ENV}.tradier.com/v1/markets/options/chains?symbol={symbol}&expiration={expiration}&greeks=true"
    options_chain = getAPIData(url)
    return options_chain

