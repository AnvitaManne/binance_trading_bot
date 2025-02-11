import json
import os
import binance_client
import binance
import strategy
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

    ETH=project_settings["Tokens"]["ETH"]
    BTCB=project_settings["Tokens"]["BTCB"]
    BUSD=project_settings["Tokens"]["BUSD"]

    account=binance_client.query_account(api_key,secret_key)
    if account['canTrade']:
        print("You can trade")
        # calculate the current ratio 
        reference_ratio = strategy.check_pair_relation(ETH, BTCB, "bsc")  # Make sure it's "bsc" not "bac"
        print(f"ETH price and BTC price for reference ratio:", reference_ratio)  # Debug print
        current_ratio = strategy.check_pair_relation(BUSD, BTCB, "bsc")
        print(f"BUSD price and BTC price for current ratio:", current_ratio)  # Debug print
        print(f"Reference ratio: {reference_ratio}")
        print(f"Current ratio: {current_ratio}")
        #calculate difference between the ratios
        check=strategy.check_ratio_relation(current_ratio,reference_ratio)
        if check:
            print("Buying time")
        else:
            print("Selling time")