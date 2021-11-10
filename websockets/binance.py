
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../../finplot')
import finplot as fplt

import json
import pandas as pd
from time import sleep
from threading import Thread
import websocket

class BinanceFutureWebsocket:
    def __init__(self):
        self.url = 'wss://fstream.binance.com/stream'
        self.symbol = None
        self.interval = None
        self.ws = None
        self.df = None

    def reconnect(self, symbol, interval, df):
        '''Connect and subscribe, if not already done so.'''
        self.df = df
        if symbol.lower() == self.symbol and self.interval == interval:
            return
        self.symbol = symbol.lower()
        self.interval = interval
        self.thread_connect = Thread(target=self._thread_connect)
        self.thread_connect.daemon = True
        self.thread_connect.start()

    def close(self, reset_symbol=True):
        if reset_symbol:
            self.symbol = None
        if self.ws:
            self.ws.close()
        self.ws = None

    def _thread_connect(self):
        self.close(reset_symbol=False)
        print('websocket connecting to %s...' % self.url)
        self.ws = websocket.WebSocketApp(self.url, on_message=self.on_message, on_error=self.on_error)
        self.thread_io = Thread(target=self.ws.run_forever)
        self.thread_io.daemon = True
        self.thread_io.start()
        for _ in range(100):
            if self.ws.sock and self.ws.sock.connected:
                break
            sleep(0.1)
        else:
            self.close()
            raise websocket.WebSocketTimeoutException('websocket connection failed')
        self.subscribe(self.symbol, self.interval)
        print('websocket connected')

    def subscribe(self, symbol, interval):
        try:
            data = '{"method":"SUBSCRIBE","params":["%s@kline_%s"],"id":1}' % (symbol, interval)
            self.ws.send(data)
        except Exception as e:
            print('websocket subscribe error:', type(e), e)
            raise e

    def on_message(self, *args, **kwargs):
        df = self.df
        if df is None:
            return
        msg = json.loads(args[-1])
        if 'stream' not in msg:
            return
        stream = msg['stream']
        if '@kline_' in stream:
            k = msg['data']['k']
            t = k['t']
            t0 = int(df.index[-2].timestamp()) * 1000
            t1 = int(df.index[-1].timestamp()) * 1000
            t2 = t1 + (t1-t0)
            if t < t2:
                # update last candle
                i = df.index[-1]
                df.loc[i, 'Close']  = float(k['c'])
                df.loc[i, 'High']   = max(df.loc[i, 'High'], float(k['h']))
                df.loc[i, 'Low']    = min(df.loc[i, 'Low'],  float(k['l']))
                df.loc[i, 'Volume'] = float(k['v'])
            else:
                # create a new candle
                data = [t] + [float(k[i]) for i in ['o','c','h','l','v']]
                candle = pd.DataFrame([data], columns='Time Open Close High Low Volume'.split()).astype({'Time':'datetime64[ms]'})
                candle.set_index('Time', inplace=True)
                self.df = df.append(candle)

    def on_error(self, error, *args, **kwargs):
        print('websocket error: %s' % error)