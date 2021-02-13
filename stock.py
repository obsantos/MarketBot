
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
    """Given a stock symbol query Yahoo Finance for details"""
    response = requests.get(YAHOO_FINANCE_URL.format(symbol)).json()
    return response

def print_symbol_details(symbol,details):
    """Prints the symbol\'s details"""
    try:
        result = details['quoteResponse']['result'][0]
        name = result['longName']
        previous = result['regularMarketPreviousClose']['fmt']
        current = result['regularMarketPrice']['fmt']
        change_percent = result['regularMarketChangePercent']['fmt']
        change = result['regularMarketChange']['fmt']
        print(name + " (" + symbol + ")")
        print("Price: " + current)
        print("Previous: " + previous + " - Change: " + change + " (" + change_percent + ")")
    except ValueError:
        print("Error parsing the JSON response")

def main():
    parser = argparse.ArgumentParser(description='Script that queries Yahoo Finance to retrieve a symbol\'s price')
    parser.add_argument('-s', '--symbol', help='Symbol you want to query', type=str, required=True)
    args = parser.parse_args()

    if not args.symbol:
        parser.print_help()
        sys.exit(1)

    json = query_symbol_details(args.symbol)
    print_symbol_details(args.symbol, json)
    

if __name__ == '__main__':
    main()