#!/usr/bin/env python

'''
    Slack bot to query price/details of a stock symbol
    Author: Omar Busto Santos 
    Date created: 02/13/2021
'''

import os
import logging
import re
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slackeventsapi import SlackEventAdapter
from flask import Flask
import stock

# Initialize a Flask app to host the events adapter
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'], "/slack/events", app)

# Initialize a Web API client
client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

def get_message_payload(msg):
    return {
        "ts": "",
        "channel": "#bots",
        "username": "Market Bot",
        "attachments": [ 
            msg
        ]
    }

def send_price_msg(details):
    """Sends price message to the channel"""    
    if details['change'].startswith('-'):
        trend = ":chart_with_downwards_trend:"
        indicator = ":red_circle:"
        color = "#FF0000"
        details['change'] = details['change'].replace("-", "-$")
    else:
        trend = ":chart_with_upwards_trend:"
        indicator = ":large_green_circle:"
        color = "#00FF00"
        details['change'] = "$" + details['change']

    msg = {
            "color": color,
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "{0} ({1}) {2}".format(details['name'], details['symbol'], indicator),
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Current Price:* ${0}".format(details['current'])
                    },
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Previous Close Price:*"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Change:*"
                        },
                        {
                            "type": "plain_text",
                            "text": "${0}".format(details['previous'])
                        },
                        {
                            "type": "plain_text",
                            "text": "{0} ({1}) {2}".format(details['change'], details['percent'], trend)
                        }
                    ]
                }
            ]
        }
    payload = get_message_payload(msg)
    response = client.chat_postMessage(**payload)

@slack_events_adapter.on("message")
def message(payload):
    """Parse channel messages looking for stock symbols"""
    event = payload.get("event", {})
    text = event.get("text")

    if text:
        symbols = re.findall(r'\$\b[a-zA-Z]+\b', text)
        for symbol in symbols:            
            details = stock.query_symbol_details(symbol[1:])
            send_price_msg(details)

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.run(port=3000)