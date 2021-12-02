import numpy as np

def rsi(Data, rsi_lookback, what1, what2):
    
    # From exponential to smoothed
    rsi_lookback = (rsi_lookback * 2) - 1  
        
    # Get the difference in price from previous step
    delta = []
   
    for i in range(len(Data)):
        try:
            diff = Data[i, what1] - Data[i - 1, what1] 
            delta = np.append(delta, diff)                  
        except IndexError:
            pass
        
    delta = np.insert(delta, 0, 0, axis = 0)               
    delta = delta[1:] 
    
    # Make the positive gains (up) and negative gains (down) Series
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    
    up = np.array(up)
    down = np.array(down)
    
    roll_up = up
    roll_down = down
    
    roll_up = np.reshape(roll_up, (-1, 1))
    roll_down = np.reshape(roll_down, (-1, 1))
    
    roll_up = adder(roll_up, 3)
    roll_down = adder(roll_down, 3)
    
    roll_up = ema(roll_up, 2, rsi_lookback, what2, 1)
    roll_down = ema(abs(roll_down), 2, rsi_lookback, what2, 1)
    
    roll_up = roll_up[rsi_lookback:, 1:2]
    roll_down = roll_down[rsi_lookback:, 1:2]
    Data = Data[rsi_lookback + 1:,]
    
    # Calculate the RS & RSI
    RS = roll_up / roll_down
    RSI = (100.0 - (100.0 / (1.0 + RS)))
    RSI = np.array(RSI)
    RSI = np.reshape(RSI, (-1, 1))
    RSI = RSI[1:,]
    
    Data = np.concatenate((Data, RSI), axis = 1)    
    return Data

def ma(Data, lookback, what, where):
    
    for i in range(len(Data)):
        try:
            Data[i, where] = (Data[i - lookback + 1:i + 1, what].mean())
        except IndexError:
            pass

        return Data

def ema(Data, alpha, lookback, what, where):
    
    # alpha is the smoothing factor
    # window is the lookback period
    # what is the column that needs to have its average calculated
    # where is where to put the exponential moving average
    
    alpha = alpha / (lookback + 1.0)
    beta  = 1 - alpha
    
    # First value is a simple SMA
    Data = ma(Data, lookback, what, where)
    
    # Calculating first EMA
    Data[lookback + 1, where] = (Data[lookback + 1, what] * alpha) + (Data[lookback, where] * beta)
    # Calculating the rest of EMA
    for i in range(lookback + 2, len(Data)):
            try:
                Data[i, where] = (Data[i, what] * alpha) + (Data[i - 1, where] * beta)
        
            except IndexError:
                pass
    return Data

# The function to add a certain number of columns
def adder(Data, times):
    
    for i in range(1, times + 1):
    
        z = np.zeros((len(Data), 1), dtype = float)
        Data = np.append(Data, z, axis = 1)            
    return Data
# The function to deleter a certain number of columns
def deleter(Data, index, times):
    
    for i in range(1, times + 1):
    
        Data = np.delete(Data, index, axis = 1)            
    return Data
# The function to delete a certain number of rows from the beginning
def jump(Data, jump):
    
    Data = Data[jump:, ]
    
    return Data


def stochastic(Data, lookback, what, high, low, where):
        
    for i in range(len(Data)):
        
        try:
          Data[i, where] = (Data[i, what] - min(Data[i - lookback + 1:i + 1, low])) / (max(Data[i - lookback + 1:i + 1, high]) - min(Data[i - lookback + 1:i + 1, low]))
        
        except ValueError:
            pass
    
    Data[:, where] = Data[:, where] * 100            
    return Data

# The Data variable refers to the OHLC array
# The lookback variable refers to the period (5, 14, 21, etc.)
# The what variable refers to the closing price
# The high variable refers to the high price
# The low variable refers to the low price
# The where variable refers to where to put the Oscillator
def stoch_rsi(Data, lookback, where):
    
    # Calculating RSI of the Closing prices
    Data = rsi(Data, lookback, 3, 0)
    
    # Adding two columns
    Data = adder(Data, 2)
    
    for i in range(len(Data)):
        
        try:
            Data[i, where + 1] = (Data[i, where] - min(Data[i - lookback + 1:i + 1, where])) / (max(Data[i - lookback + 1:i + 1, where]) - min(Data[i - lookback + 1:i + 1, where]))
        
        except ValueError:
            pass
    
    Data[:, where + 1] = Data[:, where + 1] * 100 
    
    # Signal Line using a 3-period moving average
    Data = ma(Data, 3, where + 1, where + 2)
    
    Data = deleter(Data, where, 2)
    Data = jump(Data, lookback)    
    
    return Data