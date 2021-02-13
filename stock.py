#!/usr/bin/env python

'''
    Script to query Yahoo Finance to get details of a given stock symbol
    Author: Omar Busto Santos 
    Date created: 02/13/2021
'''

import sys, argparse
import requests

YAHOO_FINANCE_URL = "https://query1.finance.yahoo.com/v7/finance/quote?formatted=true&symbols={0}&fields=regularMarketChangePercent%2CregularMarketChange%2CregularMarketPrice%2ClongName%2CshortName"

def query_symbol_details(symbol):
    """Given a stock symbol query Yahoo Finance for details and returns a simplified object"""
    response = requests.get(YAHOO_FINANCE_URL.format(symbol)).json()
    try:
        result = response['quoteResponse']['result'][0]
        name = result['longName']
        previous = result['regularMarketPreviousClose']['fmt']
        current = result['regularMarketPrice']['fmt']
        change_percent = result['regularMarketChangePercent']['fmt']
        change = result['regularMarketChange']['fmt']
        return {
            "symbol": symbol,
            "name": name,
            "previous": previous,
            "current": current,
            "change": change,
            "percent": change_percent
        }
    except ValueError:
        return {}

def print_symbol_details(details):
    """Prints the symbol\'s details"""
    print(details['name'] + " (" + details['symbol'] + ")")
    print("Price: " + details['current'])
    print("Previous: " + details['previous'] + " - Change: " + details['change'] + " (" + details['percent'] + ")")

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
