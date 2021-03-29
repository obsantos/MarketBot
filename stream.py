#!/usr/bin/env python

'''
    Script to stream stock prices from Yahoo Finance websocket
    Author: Omar Busto Santos 
    Date created: 03/26/2021
'''

import base64
import streamer_pb2
import websocket

STATE_REGULAR = "REGULAR_MARKET"
STATE_POST = "POST_MARKET"

try:
    import thread
except ImportError:
    import _thread as thread
import time

def on_message(ws, message):
    msg = base64.b64decode(message)
    market = streamer_pb2.market()
    market.ParseFromString(msg)
    print(market)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        print("### open ###")
        ws.send("{ \"subscribe\": [\"GME\"] }")
    thread.start_new_thread(run, ())

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://streamer.finance.yahoo.com/",
                              on_open = on_open,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)

    ws.run_forever()

