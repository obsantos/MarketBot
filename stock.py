#!/usr/bin/env python

'''
    Script to query Yahoo Finance to get details of a given stock symbol
    Author: Omar Busto Santos 
    Date created: 02/13/2021
'''

import sys, argparse
import requests

YAHOO_FINANCE_URL = "https://query1.finance.yahoo.com/v7/finance/quote?formatted=true&symbols={0}&fields={1}"
FIELDS = "regularMarketChangePercent%2CregularMarketChange%2CregularMarketPrice%2ClongName%2CshortName%2CmarketState%2CpostMarketChangePercent%2CpostMarketChange%2CpostMarketPrice%2CpreMarketChange%2CpreMarketPrice%2CpreMarketChangePercent"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"
MARKET_STATE_REG = "REGULAR"
MARKET_STATE_PRE = "PRE"
MARKET_STATE_POST = "POST"
MARKET_STATE_NIGHT = "POSTPOST"
MARKET_STATE_CLOSED = "CLOSED"
QUOTE_TYPE_ETF = "ETF"
QUOTE_TYPE_CRYPTO = "CRYPTOCURRENCY"
QUOTE_TYPE_INDEX = "INDEX"

headers = {
    'User-Agent': USER_AGENT
}

## Uncomment to debug
# import http.client as http_client
# http_client.HTTPConnection.debuglevel = 1

def get_price_for_market_state_crypto(state, result):
    """Returns the price for the current state of the market for Cryptocurrency symbols"""
    ## Crypto always on REGULAR market state, as it never sleeps ZZzzZZzzz...
    return {
        "current": result['regularMarketPrice']['fmt'],
        "previous": result['regularMarketPreviousClose']['fmt'],
        "change": result['regularMarketChange']['fmt'],
        "percent": result['regularMarketChangePercent']['fmt']
    } 

def get_price_for_market_state_etf(state, result):
    """Returns the price for the current state of the market for ETF symbols"""
    ## It seems that for ETF symbols it uses REGULAR market fields
    return {
        "current": result['regularMarketPrice']['fmt'],
        "previous": result['regularMarketPreviousClose']['fmt'],
        "change": result['regularMarketChange']['fmt'],
        "percent": result['regularMarketChangePercent']['fmt']
    }

def get_price_for_market_state_index(state, result):
    """Returns the price for the current state of the market for Index symbols"""
    ## It seems that for Index symbols it uses REGULAR market fields
    return {
        "current": result['regularMarketPrice']['fmt'],
        "previous": result['regularMarketPreviousClose']['fmt'],
        "change": result['regularMarketChange']['fmt'],
        "percent": result['regularMarketChangePercent']['fmt']
    }

def get_price_for_market_state_equity(state, result):
    """Returns the price for the current state of the market for equity symbols"""
    if state == MARKET_STATE_PRE:
        return {
            "current": result['preMarketPrice']['fmt'],
            "previous": result['regularMarketPrice']['fmt'],
            "change": result['preMarketChange']['fmt'],
            "percent": result['preMarketChangePercent']['fmt']
        }
    elif state == MARKET_STATE_POST or state == MARKET_STATE_NIGHT or state == MARKET_STATE_CLOSED:
        return {
            "current": result['postMarketPrice']['fmt'],
            "previous": result['regularMarketPrice']['fmt'],
            "change": result['postMarketChange']['fmt'],
            "percent": result['postMarketChangePercent']['fmt']
        }
    else:
        return {
            "current": result['regularMarketPrice']['fmt'],
            "previous": result['regularMarketPreviousClose']['fmt'],
            "change": result['regularMarketChange']['fmt'],
            "percent": result['regularMarketChangePercent']['fmt']
        } 

def get_price_for_market_state_by_quote_type(quoteType, state, result):
    """Returns the price for the current state of the market depending on the quote type"""
    if quoteType == QUOTE_TYPE_INDEX:
        return get_price_for_market_state_index(state, result)
    elif quoteType == QUOTE_TYPE_ETF:
        return get_price_for_market_state_etf(state, result)
    elif quoteType == QUOTE_TYPE_CRYPTO:
        return get_price_for_market_state_crypto(state, result)
    else: 
        return get_price_for_market_state_equity(state, result)
       
def get_symbol_name(result):
    """Returns the name used by this symbol based on availability"""
    if 'longName' in result:
        return result['longName']
    elif 'shortName' in result:
        return result['shortName']
    else:
        return result['symbol']

def query_symbol_details(symbol):
    """Given a stock symbol query Yahoo Finance for details and returns a simplified object"""
    response = requests.get(YAHOO_FINANCE_URL.format(symbol, FIELDS), headers=headers).json()
    print(response)
    try:
        result = response['quoteResponse']['result'][0]
        name = get_symbol_name(result)
        state = result['marketState']
        quoteType = result['quoteType']
        price = get_price_for_market_state_by_quote_type(quoteType, state, result)
        return {
            "symbol": symbol,
            "name": name,
            "state": state,
            "price": price,
            "quoteType": quoteType
        }
    except ValueError:
        return {}

def print_symbol_details(details):
    """Prints the symbol\'s details"""
    print(details['name'] + " (" + details['symbol'] + ") - " + details['state'])
    print("Price: " + details['price']['current'])
    print("Previous: " + details['price']['previous'] + " - Change: " + details['price']['change'] + " (" + details['price']['percent'] + ")")

def main():
    parser = argparse.ArgumentParser(description='Script that queries Yahoo Finance to retrieve a symbol\'s price')
    parser.add_argument('-s', '--symbol', help='Symbol you want to query', type=str, required=True)
    args = parser.parse_args()

    if not args.symbol:
        parser.print_help()
        sys.exit(1)

    details = query_symbol_details(args.symbol)
    print_symbol_details(details)    

if __name__ == '__main__':
    main()
