from binance.spot import Spot
import pandas

#3 functions can ensure we are connected to the binance api for spot trading


#to get status of connection to binance
def query_binance_status():
    status=Spot().system_status()
    if status["status"]==0:
        #able to connect to binance
        return True
    else:
        return ConnectionError
    
#going to use api key and secret key to get account we are using
def query_account(api_key,secret_key):
    return Spot(
        api_key=api_key,
        api_secret=secret_key,
        base_url="https://testnet.binance.vision"
    ).account()

#to check if testnet is working properly
def query_testnet():
    client=Spot(base_url="https://testnet.binance.vision")
    print(client.time())

#function to get info about the candlesticks
def get_candlestick_data(symbol,timeframe,qty):
    #get raw data
    raw_data=Spot().klines(symbol=symbol,interval=timeframe,limit=qty)
    converted_data=[]
    for candle in raw_data:
        converted_candle={
            "time":candle[0],
            "open":float(candle[1]),
            "high":float(candle[2]),
            "low":float(candle[3]),
            "close":float(candle[4]),
            "volume":float(candle[5]),
            "close_time":candle[6],
            "quote_asset_volume":float(candle[7]),
            "number_of_trades":int(candle[8]),
            "taker_buy_base_asset_volume":float(candle[9]),
            "taker_buy_quote_asset_volume":float(candle[10]),
        }
        #Add the data 
        converted_data.append(converted_candle)   
    return converted_data

#function to query all sysmbols from a base asset
def query_quote_asset_list(quote_asset_symbol):
    symbol_dictionary=Spot().exchange_info()
    #convert this into dataframe
    symbol_dataframe=pandas.DataFrame(symbol_dictionary["symbols"])
    #extract all symbols with the base asset pair(ETH)
    quote_symbol_dataframe=symbol_dataframe.loc[
        symbol_dataframe["quoteAsset"]==quote_asset_symbol
    ]
    quote_symbol_dataframe=quote_symbol_dataframe.loc[
        quote_symbol_dataframe["status"]=="TRADING"
    ]
    #ETHSHIBA 
    #need to use since binance doesnt have the trait available for trading
    return quote_symbol_dataframe

#func to make trade w params
def make_trade_with_params(parmas,project_settings):
    print("making trade with params")
    #set api key
    api_key=project_settings["BinanaceKeys"]["API_Key"]
    #set secret key
    secret_key=project_settings["BinanceKeys"]["Secret_Key"]
    #set up client
    client=Spot(
        api_key=api_key,
        api_secret=secret_key,
        base_url="https://testnet.binance.vision",
    )
    #make the trade
    try:
        response=client.new_order(**parmas)
        return response
    except ConnectionRefusedError as error:
        print(f"Error: {error}")

#func to query trades
def query_open_trades(project_settings):
    #set the api key
    api_key=project_settings["BinanceKeys"]["API_Key"]
    #set the secret key
    secret_key=project_settings["BinanceKeys"]["Secret_Key"]
    #setup the client
    client=Spot(
        api_key=api_key,
        secret_key=secret_key,
        base_url="https://testnet.binance.vision",
    )
    #get trades 
    try:
        response=client.get_open_orders()
        return response
    except ConnectionRefusedError as error:
        print(f"Error: {error}")


#func to cancel a trade
def cancel_order_by_symbol(symbol,project_settings):
    api_key=project_settings["BinanceKeys"]["API_Key"]
    secret_key=project_settings["BinanceKeys"]["Secret_Key"]
    client=Spot(
        api_key=api_key,
        secret_key=secret_key,
        base_url="https://testnet.binance.vision",
    )
    #cancel the trade 
    try:
        response=client.cancel_open_orders(symbol=symbol)
        return response
    except ConnectionRefusedError as error:
        print(f"Error: {error}")

#func to place a limit order for symbol
def place_limit_order(symbol,side,quantity,price,project_settings):
    api_key=project_settings["BinanceKeys"]["API_Key"]
    secret_key=project_settings["BinanceKeys"]["Secret_Key"]
    client=Spot(
        api_key=api_key,
        secret_key=secret_key,
        base_url="https://testnet.binance.vision",
    )
    #place the limit order
    try:
        response=client.new_order(
            symbol=symbol,
            #for buying or selling
            side=side,
            type="LIMIT",
            timeInForce="GTC",
            quanity=quantity,
            price=price,
        )
        return response
    except ConnectionRefusedError as error:
        print(f"Error: {error}")


def place_stop_loss_order(symbol,side,quantity,stop_price,limit_price,project_settings):
    api_key=project_settings["BinanceKeys"]["API_Key"]
    secret_key=project_settings["BinanceKeys"]["Secret_Key"]
    client=Spot(
        api_key=api_key,
        secret_key=secret_key,
        base_url="https://testnet.binance.vision",
    )
    #place to stop loss order
    try:
        #sending this info as new order
        response=client.new_order(
            symbol=symbol,
            #for buying or selling
            side=side,
            type="LIMIT",
            timeInForce="GTC",
            quanity=quantity,
            stop_price=stop_price,
            price=limit_price,
        )
        return response
    except ConnectionRefusedError as error:
        print(f"Error: {error}")

