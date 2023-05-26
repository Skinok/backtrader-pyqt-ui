class Singleton:
    __instance = None

    def __new__(cls,*args, **kwargs):
        if cls.__instance is None :
            cls.__instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls.__instance