import json
import os
import binance_client
import binance
from binance.spot import Spot

import_path="settings.json"

#to import settings.json for all the api keys ,secret keys..
def get_settings(import_path):
    #ensure if path exists
    if os.path.exists(import_path):
        file=open(import_path,"r")
        project_settings=json.load(file)
        file.close()
        return project_settings
    else:
        return ImportError
    
if __name__=="__main__":
    project_settings=get_settings(import_path)
    api_key=project_settings["BinanceKeys"]["API_Key"]
    secret_key=project_settings["BinanceKeys"]["Secret_Key"]

    dataframe=binance_client.query_quote_asset_list("BTC")
    print(dataframe)