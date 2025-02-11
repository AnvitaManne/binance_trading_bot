import pandas
import numpy
import binance_client
import time
import requests
#function to convert the data from binance candlestick data to a dataframe
def get_and_transform_data(symbol,timeframe,number_of_candles):
    #get the data
    raw_data=binance_client.get_candlestick_data(symbol,timeframe,number_of_candles)
    #convert the data into a dataframe
    df=pandas.DataFrame(raw_data)
    #convert the time to a readable format
    df["time"]=pandas.to_datetime(df["time"],unit="ms")
    df["close_time"]=pandas.to_datetime(df["close_time"],unit="ms")
    df["RedOrGreen"]=numpy.where(df["close"]>df["open"],"Green","Red")
    return df


def get_token_price(address, chain):
    url = f"http://localhost:5002/getPrice?address={address}&chain={chain}"
    try:
        response = requests.get(url)
        data = response.json()
        return data.get("usdPrice", 0) or 0.0001  # Return small value instead of 0
    except Exception as e:
        print(f"Error getting price: {e}")
        return 0.0001

def check_pair_relation(address1, address2, chain):
    price1 = get_token_price(address1, chain)
    price2 = get_token_price(address2, chain)
    if price1 == 0 or price2 == 0:
        print(f"Warning: Got zero price for one of the tokens")
        return None
    return price1/price2

def check_ratio_relation(current_ratio,reference_ratio):
    #calculate the difference between the ratios
    #ratio 1=TOKEN1/TOKEN3
    #ratio 2=TOKEN2/TOKEN3
    if current_ratio>reference_ratio:
        #the current ratio is greater than the reference ratio
        #consider selling token1 for token3
        return False
    elif current_ratio<reference_ratio:
        #the current ratio is less than the reference ratio
        #consider buying token1 with token3
        return True
    
#to check the consecutive raise or decrease