
import os,sys
import Singleton
import pandas as pd

from Singleton import Singleton

class DataManager(Singleton):

    def DatetimeFormat(self, dataFilePath):
        fileparts = os.path.split(dataFilePath)
        datafile = fileparts[1]
        # print(datafile[-4:])
        if datafile[-4:]=='.csv':
            df = pd.read_csv(dataFilePath, nrows=1)
            
            timestring = df.iloc[0,0]
            ncolon = timestring.count(':')
            if ncolon==2:
                return "%Y-%m-%d %H:%M:%S"
            elif ncolon==1:
                return "%Y-%m-%d %H:%M"
            else:
                nspace = timestring.count(' ')
                if nspace==1:
                    return "%Y-%m-%d %H"
                else:
                    return "%Y-%m-%d"
                
        return ""


    # Return True if loading is successfull & the error string if False
    # dataPath is the full file path
    def loadDataFrame(self, loadDataFile):

        # Try importing data file
        # We should code a widget that ask for options as : separators, date format, and so on...
        try:

            # Python contains
            if pd.__version__<'2.0.0':
                df = pd.read_csv(loadDataFile.filePath, 
                                    sep=loadDataFile.separator, 
                                    parse_dates=[0], 
                                    date_parser=lambda x: pd.to_datetime(x, format=loadDataFile.timeFormat), 
                                    skiprows=0, 
                                    header=0, 
                                    names=["Time", "Open", "High", "Low", "Close", "Volume"],
                                    index_col=0)
            else:
                df = pd.read_csv(loadDataFile.filePath,
                                    sep=loadDataFile.separator, 
                                    parse_dates=[0], 
                                    date_format=loadDataFile.timeFormat, 
                                    skiprows=0, 
                                    header=0, 
                                    names=["Time", "Open", "High", "Low", "Close", "Volume"],
                                    index_col=0)

            return df, ""

        except ValueError as err:
            return None, "ValueError error:" + str(err)
        except AttributeError as err:
            return None, "AttributeError error:" + str(err)
        except IndexError as err:
            return None, "IndexError error:" + str(err)
        except :
            return None, "Unexpected error:" + str(sys.exc_info()[0])
        

    def findTimeFrame(self, df):

        if len(df.index) > 2:
            dtDiff = df.index[1] - df.index[0]

            if dtDiff.total_seconds() == 60:
                return "M1"
            elif dtDiff.total_seconds() == 300:
                return "M5"
            elif dtDiff.total_seconds() == 900:
                return "M15"
            elif dtDiff.total_seconds() == 1800:
                return "M30"
            elif dtDiff.total_seconds() == 3600:
                return "H1"
            elif dtDiff.total_seconds() == 14400:
                return "H4"
            elif dtDiff.total_seconds() == 86400:
                return "D"
            elif dtDiff.total_seconds() == 604800:
                return "W"

        pass