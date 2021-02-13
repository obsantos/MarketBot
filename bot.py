#!/usr/bin/env python

'''
    Slack bot to query price/details of a stock symbol
    Author: Omar Busto Santos 
    Date created: 02/13/2021
'''

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import stock

client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

def get_message_payload(msg):
    return {
        "ts": "",
        "channel": "#bots",
        "username": "Market Bot",
        "blocks": msg,
    }

def send_price_msg(details):
    """Sends price message to the channel"""    
    if details['change'].startswith('-'):
        trend = ":chart_with_downwards_trend:"
        indicator = ":red_circle:"
    else:
        trend = ":chart_with_upwards_trend:"
        indicator = ":large_green_circle:"

    msg = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "{0} ({1}) {2}".format(details['name'], details['symbol'], trend),
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Current Price:* ${0}".format(details['current'])
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "*Previous Close Price:* ${0}".format(details['previous'])
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Change:* ${0} ({1}) {2}".format(details['change'], details['percent'], indicator)
                    }
                ]
            }
        ]
    payload = get_message_payload(msg)
    response = client.chat_postMessage(**payload)

details = stock.query_symbol_details("GME")
send_price_msg(details) 