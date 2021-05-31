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

# Timestamp of the latest message processed
# NOTE: Mainly for heroku since the service dies after 1h on the free tier and when waking up it sometimes it gets older messages
last_processed = 0

def check_processed(ts):
    """Checks if a timestamp of a message is newer than the last processed"""
    global last_processed
    if ts > last_processed:
        last_processed = ts
        return True
    return False

def get_message_payload(channel_id, msg):
    """Gets the message payload to be sent in the post message api"""
    return {
        "ts": "",
        "channel": channel_id,
        "username": "Market Bot",
        "attachments": [ 
            msg
        ]
    }

def sanitize_message(msg):
    """Sanitizes the message removing possible http link formating"""
    http_prefix = "$<http://"
    if msg.startswith(http_prefix):
        index = msg.find("|")
        return "$" + msg[len(http_prefix):index]
    return msg

def send_price_msg(channel_id, details):
    """Sends price message to the channel"""    
    if details['price']['change'].startswith('-'):
        trend = ":chart_with_downwards_trend:"
        indicator = ":red_circle:"
        color = "#FF0000"
        details['price']['change'] = details['price']['change'].replace("-", "-$")
    else:
        trend = ":chart_with_upwards_trend:"
        indicator = ":large_green_circle:"
        color = "#00FF00"
        details['price']['change'] = "+$" + details['price']['change']

    # Override color, emojis and some text if we are in pre/post market
    if details['state'] == stock.MARKET_STATE_PRE:
        color = "#FFFF00"
        indicator = ":hatching_chick:"
        current_text = "Pre-Market price"
        previous_text = "Market close price"
    elif details['state'] == stock.MARKET_STATE_POST:
        color = "#777777"
        indicator = ":new_moon_with_face:"
        current_text = "After Hours price"
        previous_text = "Market close price"
    elif details['state'] == stock.MARKET_STATE_NIGHT or details['state'] == stock.MARKET_STATE_CLOSED:
        color = "#777777"
        indicator = ":sleeping:"
        current_text = "After Hours close price"
        previous_text = "Market close price"
    else:
        current_text = "Market price"
        previous_text = "Previous close price"

    msg = {
            "color": color,
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "{0} ({1})  {2}".format(details['name'], details['symbol'].upper(), indicator),
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*{0}:*".format(current_text)
                        },
                        {
                            "type": "plain_text",
                            "text": "${0}".format(details['price']['current'])
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*{0}:*".format(previous_text)
                        },
                        {
                            "type": "plain_text",
                            "text": "${0}".format(details['price']['previous'])
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Change:*"
                        },
                        {
                            "type": "plain_text",
                            "text": "{0} ({1}) {2}".format(details['price']['change'], details['price']['percent'], trend)
                        }
                    ]
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "More information <https://finance.yahoo.com/quote/{0}|here>".format(details['symbol'])
                        }
                    ]
                }
            ]
        }
    payload = get_message_payload(channel_id, msg)
    client.chat_postMessage(**payload)

@slack_events_adapter.on("message")
def message(payload):
    """Parse channel messages looking for stock symbols"""
    event = payload.get("event", {})
    text = sanitize_message(event.get("text"))
    channel_id = event.get("channel")
    ts = payload.get("event_time")

    if check_processed(ts) and text:
        symbols = re.findall(r'\$\b[a-zA-Z.-]+\b', text)
        for symbol in symbols:            
            details = stock.query_symbol_details(symbol[1:])
            send_price_msg(channel_id, details)

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)