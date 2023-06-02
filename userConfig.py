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

    def saveObject(self, name, obj):

        obj_dict = {}

        # Get all objects attributes and store them in the config file
        # https://stackoverflow.com/questions/11637293/iterate-over-object-attributes-in-python
        for attributeName in [a for a in dir(obj) if not a.startswith('__') and not callable(getattr(obj, a))]:

            # we should use decorator here instead of a hardcoded
            if attributeName != "dataFrame":
                obj_dict[attributeName] = getattr(obj, attributeName)

        self.data[name] = obj_dict

        self.saveConfig()
        pass

    def saveParameter(self, parameter, value):
        self.data[parameter] = value
        self.saveConfig()
        pass

    def removeParameter(self, parameter):
        if parameter in self.data[parameter]:
            del self.data[parameter]
        self.saveConfig()
        pass
    
    def saveConfig(self):
        try:
            with open("userData.json", "w+") as userFile:
                json.dump(self.data, userFile, indent = 4)
        except:
            print(" Can't save user config file")


