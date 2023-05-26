

# Après avoir importé les librairies nécessaires
class OandaV20Connector(OandaV20Store):
    # Le constructeur de la classe
    def __init__(self, token, account, practice=True):
        # Appelle le constructeur de la classe parente
        super().__init__(token=token, account=account, practice=practice)
        # Crée un broker à partir du store
        self.broker = self.getbroker()
        # Crée un data feed à partir du store
        self.data = self.getdata(dataname="EUR_USD", timeframe=bt.TimeFrame.Minutes, compression=1)

    # Une méthode pour ajouter le data feed au Cerebro
    def add_data(self, cerebro):
        cerebro.adddata(self.data)

    # Une méthode pour ajouter le broker au Cerebro
    def add_broker(self, cerebro):
        cerebro.setbroker(self.broker)
