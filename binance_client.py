from binance.spot import Spot
import pandas

# 3 functions can ensure we are connected to the Binance API for spot trading

# To get status of connection to Binance
def query_binance_status():
    status = Spot().system_status()
    if status["status"] == 0:
        # Able to connect to Binance
        return True
    else:
        return ConnectionError
    
# Going to use API key and secret key to get account we are using
def query_account(api_key, secret_key):
    return Spot(
        api_key=api_key,
        api_secret=secret_key,
        base_url="https://testnet.binance.vision"
    ).account()

# To check if testnet is working properly
def query_testnet():
    client = Spot(base_url="https://testnet.binance.vision")
    print(client.time())

# Function to get info about the candlesticks
def get_candlestick_data(symbol, timeframe, qty):
    # Get raw data
    raw_data = Spot().klines(symbol=symbol, interval=timeframe, limit=qty)
    converted_data = []
    for candle in raw_data:
        converted_candle = {
            "time": candle[0],
            "open": float(candle[1]),
            "high": float(candle[2]),
            "low": float(candle[3]),
            "close": float(candle[4]),
            "volume": float(candle[5]),
            "close_time": candle[6],
            "quote_asset_volume": float(candle[7]),
            "number_of_trades": int(candle[8]),
            "taker_buy_base_asset_volume": float(candle[9]),
            "taker_buy_quote_asset_volume": float(candle[10]),
        }
        # Add the data 
        converted_data.append(converted_candle)   
    return converted_data

# Function to query all symbols from a base asset
def query_quote_asset_list(quote_asset_symbol):
    symbol_dictionary = Spot().exchange_info()
    # Convert this into dataframe
    symbol_dataframe = pandas.DataFrame(symbol_dictionary["symbols"])
    # Extract all symbols with the base asset pair
    quote_symbol_dataframe = symbol_dataframe.loc[
        symbol_dataframe["quoteAsset"] == quote_asset_symbol
    ]
    quote_symbol_dataframe = quote_symbol_dataframe.loc[
        quote_symbol_dataframe["status"] == "TRADING"
    ]
    return quote_symbol_dataframe

# Function to round price based on tick size
def round_price(symbol, price, client):
    """ Fetches the tick size and rounds price accordingly. """
    exchange_info = client.exchange_info()
    
    for pair in exchange_info["symbols"]:
        if pair["symbol"] == symbol:
            tick_size = float(pair["filters"][0]["tickSize"])
            precision = str(tick_size)[::-1].find('.')
            return round(price, precision)  # Round price correctly
    
    return price  # Fallback if no tick size found

# Function to make trade with params
def make_trade_with_params(params, project_settings):
    print("Making trade with params...")

    api_key = project_settings["BinanceKeys"]["API_Key"]
    secret_key = project_settings["BinanceKeys"]["Secret_Key"]

    client = Spot(
        api_key=api_key,
        api_secret=secret_key,
        base_url="https://testnet.binance.vision",
    )

    # Fix precision issue
    if "price" in params:
        params["price"] = str(round_price(params["symbol"], float(params["price"]), client))

    # Make the trade
    try:
        response = client.new_order(**params)
        return response
    except Exception as error:
        print(f"Trade failed: {error}")
        return None

# Function to query open trades
def query_open_trades(project_settings):
    api_key = project_settings["BinanceKeys"]["API_Key"]
    secret_key = project_settings["BinanceKeys"]["Secret_Key"]

    client = Spot(
        api_key=api_key,
        api_secret=secret_key,
        base_url="https://testnet.binance.vision",
    )
    # Get trades 
    try:
        response = client.get_open_orders()
        return response
    except ConnectionRefusedError as error:
        print(f"Error: {error}")

# Function to cancel a trade
def cancel_order_by_symbol(symbol, project_settings):
    api_key = project_settings["BinanceKeys"]["API_Key"]
    secret_key = project_settings["BinanceKeys"]["Secret_Key"]

    client = Spot(
        api_key=api_key,
        api_secret=secret_key,
        base_url="https://testnet.binance.vision",
    )
    # Cancel the trade 
    try:
        response = client.cancel_open_orders(symbol=symbol)
        return response
    except ConnectionRefusedError as error:
        print(f"Error: {error}")

# Function to place a limit order for a symbol
def place_limit_order(symbol, side, quantity, price, project_settings):
    api_key = project_settings["BinanceKeys"]["API_Key"]
    secret_key = project_settings["BinanceKeys"]["Secret_Key"]

    client = Spot(
        api_key=api_key,
        api_secret=secret_key,
        base_url="https://testnet.binance.vision",
    )

    # Fix price precision issue
    price = str(round_price(symbol, float(price), client))

    # Place the limit order
    try:
        response = client.new_order(
            symbol=symbol,
            side=side,  # Buying or selling
            type="LIMIT",
            timeInForce="GTC",
            quantity=quantity,
            price=price,
        )
        return response
    except ConnectionRefusedError as error:
        print(f"Error: {error}")

# Function to place a stop-loss order
def place_stop_loss_order(symbol, side, quantity, stop_price, limit_price, project_settings):
    api_key = project_settings["BinanceKeys"]["API_Key"]
    secret_key = project_settings["BinanceKeys"]["Secret_Key"]

    client = Spot(
        api_key=api_key,
        api_secret=secret_key,
        base_url="https://testnet.binance.vision",
    )

    # Fix price precision issues
    stop_price = str(round_price(symbol, float(stop_price), client))
    limit_price = str(round_price(symbol, float(limit_price), client))

    # Place the stop-loss order
    try:
        response = client.new_order(
            symbol=symbol,
            side=side,  # Buying or selling
            type="STOP_LOSS_LIMIT",
            timeInForce="GTC",
            quantity=quantity,
            stopPrice=stop_price,
            price=limit_price,
        )
        return response
    except ConnectionRefusedError as error:
        print(f"Error: {error}")
