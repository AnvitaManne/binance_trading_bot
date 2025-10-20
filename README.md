
# Binance Trading Bot

This project is an automated cryptocurrency trading bot that integrates with the Binance Testnet and Moralis API. It simulates buying and selling tokens based on live price data and trading strategies defined in Python.

## Project Structure
```

binance_trading_bot/
│
├── app.py                   # Flask API that connects to Moralis for token prices
├── binance_client.py        # Handles Binance API calls (account, orders, candles, etc.)
├── strategy.py              # Defines trading logic and signal generation
├── main.py                  # Orchestrates trading operations using all modules
├── settings.json            # Stores Binance API keys and token addresses
├── .env                     # Contains Moralis API key
└── **pycache**/             # Auto-generated compiled files

````

## Features
- Real-time token price fetching using the Moralis API  
- Binance Testnet integration for safe simulated trading  
- Automated trading strategy execution based on market conditions  
- Dynamic trade parameter calculations using tick size and step size  
- Modular design for easier debugging and customization  

## How It Works

### 1. Price Fetching (`app.py`)
A Flask API runs locally and queries Moralis for a given token’s USD price on a specific blockchain (e.g., BSC).

Example:
```bash
GET http://localhost:5002/getPrice?address=<token_address>&chain=bsc
````

### 2. Binance Connection (`binance_client.py`)

Handles all Binance Testnet API operations such as:

* Verifying account status
* Fetching candlestick data
* Placing and canceling limit or stop-loss orders
* Querying open trades and symbols

### 3. Strategy (`strategy.py`)

Implements the trading logic:

* Retrieves recent candlestick data and converts it to a readable format
* Detects three consecutive green or red candles as potential buy/sell signals
* Compares token ratios (e.g., ETH/BTCB vs BUSD/BTCB) to identify undervalued or overvalued assets
* Automatically rounds prices and quantities according to Binance rules

### 4. Main Script (`main.py`)

The central controller:

* Loads credentials and token addresses from `settings.json`
* Confirms connectivity with Binance Testnet
* Calculates reference and current ratios between tokens
* Determines whether to buy or sell based on the comparison
* Executes trades if the analysis conditions are met

## Example Execution Flow

1. Start the Flask service:

   ```bash
   python app.py
   ```

   Output:

   ```
   * Running on http://127.0.0.1:5002/
   ```

2. Run the trading bot:

   ```bash
   python main.py
   ```

   Example output:

   ```
   You can trade
   ETH price and BTC price for reference ratio: 15.32
   BUSD price and BTC price for current ratio: 15.10
   Buying time
   Buying ETH
   ```

## Strategy Summary

| Condition                         | Action      | Description               |
| --------------------------------- | ----------- | ------------------------- |
| `current_ratio < reference_ratio` | Buy         | Token appears undervalued |
| `current_ratio > reference_ratio` | Sell        | Token appears overvalued  |
| 3 consecutive green candles       | Buy signal  | Indicates upward momentum |
| 3 consecutive red candles         | Sell signal | Indicates downward trend  |

## Configuration

### `.env`

```
MORALIS_API_KEY=your_moralis_api_key_here
```

### `settings.json`

```json
{
  "BinanceKeys": {
    "API_Key": "****",
    "Secret_Key": "****"
  },
  "Tokens": {
    "BUSD": "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56",
    "ETH": "0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
    "BTCB": "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c"
  }
}
```

## Testing and Output Examples

* Successfully connects to Binance Testnet
* Displays balances for each token
* Confirms trading permissions (`canTrade = True`)
* Retrieves all pairs available for trading against BTC
* Fetches real-time token prices through Moralis

Example log:

```
Successfully connected to Binance
Shows balance of each token
'canTrade' = True means trading is available
True at the end confirms Binance Testnet connection
```

## Notes

* Always use the Binance Testnet keys when testing.
* The current logic uses a basic price and candle-based pattern strategy.

## Requirements

* Python 3.9 or higher
* Dependencies:

  ```
  Flask
  requests
  python-binance
  moralis
  python-dotenv
  pandas
  numpy
  ```

Install them with:

```bash
pip install -r requirements.txt
```

## Author

**Anvita Manne**

## License

This project is licensed under the MIT License. You are free to use and modify it.
