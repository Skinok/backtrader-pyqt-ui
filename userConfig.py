import json
from Singleton import Singleton

class UserConfig(Singleton):

    def __init__(self):
        self.data = {}
        pass

    def loadConfigFile(self):
        try:
            with open("userData.json") as userFile:
                self.data = json.load(userFile)
        except:
            print(" Can't load user config file")

    def saveParameter(self, parameter, value):
        self.data[parameter] = value
        self.saveConfig()
        pass
    
    def saveConfig(self):
        try:
            with open("userData.json", "w+") as userFile:
                json.dump(self.data, userFile, indent = 4)
        except:
            print(" Can't save user config file")


