from backtrader import bt

class BollingerBandsBandwitch(bt.ind.BollingerBands):

    '''
    Extends the Bollinger Bands with a Percentage line and a Bandwitch indicator
    '''
    lines = ('bandwitch',)
    plotlines = dict(bandwitch=dict(_name='%Bwtch'))  # display the line as %B on chart

    def __init__(self):
        super(BollingerBandsBandwitch, self).__init__()
        self.l.bandwitch = 100 * (self.l.top - self.l.bot) / self.l.mid
        pass