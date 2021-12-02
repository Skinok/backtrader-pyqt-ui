#!/usr/bin/env python3
import numpy as np

from math import nan

def calc_parabolic_sar(df, af=0.2, steps=10):
    up = True
    sars = [nan] * len(df)
    sar = ep_lo = df.Low.iloc[0]
    ep = ep_hi = df.High.iloc[0]
    aaf = af
    aaf_step = aaf / steps
    af = 0
    for i,(hi,lo) in enumerate(zip(df.High, df.Low)):
        # parabolic sar formula:
        sar = sar + af * (ep - sar)
        # handle new extreme points
        if hi > ep_hi:
            ep_hi = hi
            if up:
                ep = ep_hi
                af = min(aaf, af+aaf_step)
        elif lo < ep_lo:
            ep_lo = lo
            if not up:
                ep = ep_lo
                af = min(aaf, af+aaf_step)
        # handle switch
        if up:
            if lo < sar:
                up = not up
                sar = ep_hi
                ep = ep_lo = lo
                af = 0
        else:
            if hi > sar:
                up = not up
                sar = ep_lo
                ep = ep_hi = hi
                af = 0
        sars[i] = sar
    df['sar'] = sars
    return df['sar']


def calc_rsi(df, n=14):
    diff = df.Close.diff().values
    gains = diff
    losses = -diff
    gains[~(gains>0)] = 0.0
    losses[~(losses>0)] = 1e-10 # we don't want divide by zero/NaN
    m = (n-1) / n
    ni = 1 / n
    g = gains[n] = gains[:n].mean()
    l = losses[n] = losses[:n].mean()
    gains[:n] = losses[:n] = nan
    for i,v in enumerate(gains[n:],n):
        g = gains[i] = ni*v + m*g
    for i,v in enumerate(losses[n:],n):
        l = losses[i] = ni*v + m*l
    rs = gains / losses
    rsi = 100 - (100/(1+rs))
    return rsi


def calc_stochastic_oscillator(df, n=14, m=3, smooth=3):
    lo = df.Low.rolling(n).min()
    hi = df.High.rolling(n).max()
    k = 100 * (df.Close-lo) / (hi-lo)
    d = k.rolling(m).mean()
    return k, d


def calc_stochasticRsi_oscillator(df, n=14, m=3, smooth=3):
    lo = df.Low.rolling(n).min()
    hi = df.High.rolling(n).max()
    k = 100 * (df.Close-lo) / (hi-lo)
    d = k.rolling(m).mean()
    return k, d


# calculating RSI (gives the same values as TradingView)
# https://stackoverflow.com/questions/20526414/relative-strength-index-in-python-pandas
def RSI(series, period=14):
    delta = series.diff().dropna()
    ups = delta * 0
    downs = ups.copy()
    ups[delta > 0] = delta[delta > 0]
    downs[delta < 0] = -delta[delta < 0]
    ups[ups.index[period-1]] = np.mean( ups[:period] ) #first value is sum of avg gains
    ups = ups.drop(ups.index[:(period-1)])
    downs[downs.index[period-1]] = np.mean( downs[:period] ) #first value is sum of avg losses
    downs = downs.drop(downs.index[:(period-1)])
    rs = ups.ewm(com=period-1,min_periods=0,adjust=False,ignore_na=False).mean() / \
         downs.ewm(com=period-1,min_periods=0,adjust=False,ignore_na=False).mean() 
    return 100 - 100 / (1 + rs)


# calculating Stoch RSI (gives the same values as TradingView)
# https://www.tradingview.com/wiki/Stochastic_RSI_(STOCH_RSI) 
def StochRSI(series, period=14, smoothK=3, smoothD=3):
    # Calculate RSI 
    delta = series.diff().dropna()
    ups = delta * 0
    downs = ups.copy()
    ups[delta > 0] = delta[delta > 0]
    downs[delta < 0] = -delta[delta < 0]
    ups[ups.index[period-1]] = np.mean( ups[:period] ) #first value is sum of avg gains
    ups = ups.drop(ups.index[:(period-1)])
    downs[downs.index[period-1]] = np.mean( downs[:period] ) #first value is sum of avg losses
    downs = downs.drop(downs.index[:(period-1)])
    rs = ups.ewm(com=period-1,min_periods=0,adjust=False,ignore_na=False).mean() / \
         downs.ewm(com=period-1,min_periods=0,adjust=False,ignore_na=False).mean() 
    rsi = 100 - 100 / (1 + rs)

    # Calculate StochRSI 
    stochrsi  = (rsi - rsi.rolling(period).min()) / (rsi.rolling(period).max() - rsi.rolling(period).min())
    stochrsi_K = stochrsi.rolling(smoothK).mean()
    stochrsi_D = stochrsi_K.rolling(smoothD).mean()

    return stochrsi, stochrsi_K, stochrsi_D