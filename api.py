# API operations
# Utilizes the Tradier API - https://documentation.tradier.com/brokerage-api

import config
import requests
import json
import time

#Switch environment
ENV = "sandbox"
#ENV = "api"

RATE_LIMIT = 170

def isSandbox(): return (ENV == "sandbox")

#Retrieve data from url endpoint
def getAPIData(url):
    bearer_token = f"Bearer {config.API_TOKEN}"
    headers={'Authorization': bearer_token, 'Accept': 'application/json'}
    response = requests.get(url, headers=headers)
    rate_avail_str = response.headers['X-Ratelimit-Available']
    rate_avail = int(rate_avail_str)
    if (rate_avail <= RATE_LIMIT):
        time.sleep(3)
    print(rate_avail)   #Use this to determine if being rate-limited
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))

def getLastStockPrice(symbol):
    url = f"https://{ENV}.tradier.com/v1/markets/quotes?symbols={symbol}"
    #print(f"{url}")
    quote_data = getAPIData(url)
    last_price = -1
    if ('quote' in quote_data['quotes']):
        last_price = quote_data['quotes']['quote']['last']
    
    return last_price

def getOptionExpirations(symbol):
    url = f"https://{ENV}.tradier.com/v1/markets/options/expirations?symbol={symbol}"
    expirations_data = getAPIData(url)
    expirations = []
    if (expirations_data['expirations']):
        expirations = expirations_data['expirations']['date']
    
    return expirations

def getOptionsChain(symbol, expiration):
    #Endpoint for options chain
    url = f"https://{ENV}.tradier.com/v1/markets/options/chains?symbol={symbol}&expiration={expiration}&greeks=true"
    options_chain_data = getAPIData(url)
    options_chain_list = options_chain_data['options']['option']
    return options_chain_list

