from flask import Flask,request,jsonify
from moralis import evm_api
from dotenv import load_dotenv
import datetime
import locale
import os

load_dotenv()
api_key=os.getenv("MORALIS_API_KEY")

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
app=Flask(__name__)

@app.route("/getPrice", methods=["GET"])
def prices():
    address = request.args.get("address")
    chain = request.args.get("chain")

    if not address or not chain:
        return jsonify({"error": "Missing parameters"}), 400

    params = {
        "chain": chain,
        "exchange": "pancakeswap-v2",
        "address": address,
    }
    try:
        result = evm_api.token.get_token_price(api_key=api_key, params=params)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    app.run(port=5002, debug=True, threaded=True)