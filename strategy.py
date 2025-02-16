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
def determine_trade_event(symbol,timeframe,percentage_change,candle_color):
    print(f"Fetching data for symbol: {symbol}")
    candlestick_data = get_and_transform_data(symbol, timeframe, 3)

    print("Candlestick Data:")
    print(candlestick_data)

    if len(candlestick_data) < 3:
        print("Not enough data for analysis.")
        return False

    if (
        candlestick_data.loc[0,"RedOrGreen"]==candle_color 
        and candlestick_data.loc[1,"RedOrGreen"]==candle_color
        and candlestick_data.loc[2,"RedOrGreen"]==candle_color
    ):


        
        #determine the percentage change
        change_one=determine_percent_change(
            candlestick_data.loc[0,"open"],candlestick_data.loc[0,"close"]
        )
        change_two=determine_percent_change(
            candlestick_data.loc[1,"open"],candlestick_data.loc[1,"close"]
        )
        change_three=determine_percent_change(
            candlestick_data.loc[2,"open"],candlestick_data.loc[2,"close"]
        )
        if candle_color=="Red":
            print(f"First drop: {change_one}")
            print(f"Second drop: {change_two}")
            print(f"Third drop: {change_three}")
        elif candle_color=="Green":
            print(f"First raise: {change_one}")
            print(f"Second raise: {change_two}")
            print(f"Third raise: {change_three}")

        #compare price changes against stated percentage change
        #the minimum threshold of increase or decrease 
        #in order to make the sell/buy worth it
        if(change_one>=percentage_change and change_two>=percentage_change and change_three>=percentage_change):
            #we can trade
            return True
        else:
            #we cant trade
            return False

def determine_percent_change(close_previous,close_current):
    return (close_current-close_previous)/close_previous

def analyse_symbols(symbol_dataframe,timeframe,percentage_change,type):
    #iterate through all symbols
    for index in symbol_dataframe.index:
        #ananlyse symbol
        if type=="buy":
            symbol = symbol_dataframe.loc[index, "symbol"]  # Extract string symbol
            analysis = determine_trade_event(symbol, timeframe,percentage_change, "Green")


            if analysis:
                print(f'{symbol_dataframe.loc[index, "symbol"]} has 3 consecutive rises')
            else:
                print(f'{symbol_dataframe["symbol"][index]} does not have 3 consecutive rises')
            
            #sleep 1 sec
            time.sleep(1)
            return analysis

def round_to_tick_size(price, tick_size):
    return round(price / tick_size) * tick_size  # Ensures valid precision

def calculate_buy_params(symbol, pair, timeframe):
    raw_data = binance_client.get_candlestick_data(symbol, timeframe, 1)
    precision = pair.iloc[0]["baseAssetPrecision"]
    filters = pair.iloc[0]["filters"]

    for f in filters:
        if f["filterType"] == "PRICE_FILTER":
            tick_size = float(f["tickSize"])
        elif f["filterType"] == "LOT_SIZE":
            min_qty = float(f["minQty"])
            step_size = float(f["stepSize"])

    close_price = raw_data[0]["close"]
    buy_stop = close_price * 1.01  # Buying at 1% higher
    buy_stop = round_to_tick_size(buy_stop, tick_size)  # Fix precision

    raw_quantity = 0.1 / buy_stop
    quantity = max(min_qty, round(raw_quantity - (raw_quantity % step_size), precision))

    params = {
        "symbol": symbol,
        "side": "BUY",
        "type": "STOP_LOSS_LIMIT",
        "timeInForce": "GTC",
        "quantity": quantity,
        "price": buy_stop,
        "trailingDelta": 100,
    }
    return params


#selling the params function
def calculate_sell_params(symbol, pair, timeframe):
    # Retrieve the candle data
    raw_data = binance_client.get_candlestick_data(symbol, timeframe, 1)

    # Determine the precision
    precision = pair.iloc[0]["baseAssetPrecision"]

    # Extract filters
    filters = pair.iloc[0]["filters"]

    # Initialize variables
    min_qty, step_size, tick_size = None, None, None

    # Loop through filters to find relevant values
    for f in filters:
        if f["filterType"] == "LOT_SIZE":
            min_qty = float(f["minQty"])
            step_size = float(f["stepSize"])
        elif f["filterType"] == "PRICE_FILTER":
            tick_size = float(f["tickSize"])  # Fix: Extract tick_size here

    # Ensure tick_size is properly retrieved
    if tick_size is None:
        raise ValueError("tick_size not found in filters")

    # Calculate the close price
    close_price = raw_data[0]["close"]

    # Calculate the sell stop price (1% below the last close price)
    sell_stop = close_price * 0.99

    # Round the sell stop price to the nearest tick size
    sell_stop = round(sell_stop / tick_size) * tick_size

    # Calculate the quantity
    raw_quantity = 0.1 / sell_stop

    # Round quantity according to step size and min_qty
    quantity = max(min_qty, round(raw_quantity - (raw_quantity % step_size), precision))

    # Construct the order parameters
    params = {
        "symbol": symbol,
        "side": "SELL",
        "type": "STOP_LOSS_LIMIT",
        "timeInForce": "GTC",
        "quantity": quantity,
        "price": sell_stop,
        "trailingDelta": 100,
    }

    return params
