#!/usr/bin/env python3

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
