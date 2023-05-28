
import pandas as pd
from pandas import DataFrame
import os




class code_file_basics():
    """
    This object stores all paths for a defined storage place.
    """
    def __init__(self, storage_name:str, directory = None):

        if not directory:
            directory = self.setting_up_data_directory()

        self.directory = directory
        self.storage_name = storage_name
        self.directory_input = directory + storage_name + "/01_raw_data/"
        self.directory_processing = directory + storage_name + "/02_processing/"
        self.directory_processing_temp = directory + storage_name + "/02_processing/temp/"
        self.directory_output = directory + storage_name + "/03_output/"

        for key in self.__dict__.keys():
            path = self.__dict__[key]
            if not os.path.exists(path):
                os.makedirs(path)

    def print_paths(self):
        """
        This function prints all paths.
        """
        for key in self.__dict__.keys():
            path = self.__dict__[key]
            print(key, " -- ", path)


    def setting_up_data_directory(self):
        """
        Looks for data directory paths.
        """
        paths = ["/Volumes/Research/e01_Amazon/02_empirics/"] #Add data directories 
        check = False
        for path in paths:
            if os.path.exists(path):
                check = True
                break 
        if check:
            print(f"The data directory is: {path}")
            return path
        else: 
            print("Could not identify a data directoy")





def data_import_keepa(path:str, data_type:str, start_date:str, end_date:str, start_listed_year:int, end_listed_year:int):
    """ 
    This function imports Keepa.com data. If data_type is set to "all", the function imports all fields. Otherwise, it only imports 'asin', 'YYWW', 'rating', 'ratingCount', 'salesRank', 'price', 'category', 'classic', and 'listedY'.
    
    """
    if data_type == "all":
        df = pd.read_csv(path, converters={'asin': lambda x: str(x)}) 
    else:
        fields = ['asin', 'YYWW', 'rating', 'ratingCount', 'salesRank', 'price', 'category', 'classic', 'listedY']
        df = pd.read_csv(path,  usecols=fields, converters={'asin': lambda x: str(x)}) 

    df = df[(df['YYWW'] >= start_date) & (df['YYWW'] <= end_date) ]
    df = df[(df['listedY'] >= start_listed_year) & (df['listedY'] <= end_listed_year) ]
    df = df.drop_duplicates()
    df['YY'] = df['YYWW'].str[0:4].astype(int)
    df['years'] = df['YY'] - df['listedY']
    return df


