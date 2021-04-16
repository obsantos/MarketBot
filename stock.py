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
MARKET_STATE_REG = "REGULAR"
MARKET_STATE_PRE = "PRE"
MARKET_STATE_POST = "POST"
MARKET_STATE_NIGHT = "POSTPOST"

def get_price_for_market_state(state, result):
    """Returns the price for the current state of the market"""
    if state == MARKET_STATE_PRE:
        return {
            "current": result['preMarketPrice']['fmt'],
            "previous": result['regularMarketPrice']['fmt'],
            "change": result['preMarketChange']['fmt'],
            "percent": result['preMarketChangePercent']['fmt']
        }
    elif state == MARKET_STATE_POST or state == MARKET_STATE_NIGHT:
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
        

def query_symbol_details(symbol):
    """Given a stock symbol query Yahoo Finance for details and returns a simplified object"""
    response = requests.get(YAHOO_FINANCE_URL.format(symbol, FIELDS)).json()
    try:
        result = response['quoteResponse']['result'][0]
        name = result['longName'] if ('longName' in result)   else symbol
        state = result['marketState']
        price = get_price_for_market_state(state, result)
        return {
            "symbol": symbol,
            "name": name,
            "state": state,
            "price": price
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
