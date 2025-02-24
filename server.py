from flask import Flask, request, jsonify
import requests
import time
import hmac
import hashlib

app = Flask(__name__)

# 🔥 Binance API 키 (여기에 본인의 API 키 입력!)
API_KEY = "0vrZraQwSLXVEQJl1JEklTVg70QBGHFo4powYdr6XNaCiAYNFWKfp7J96sKXnLpQ"
API_SECRET = "HvJI1dpzuKwVqvnaJgDv4lRVNDEgwjvrriXIaktYnde7OCE4uGDq9Doa787Mpf4s"

BINANCE_FUTURES_URL = "https://fapi.binance.com"

# 📌 Binance 선물 주문 실행 함수
def place_order(symbol, side, quantity):
    endpoint = "/fapi/v1/order"
    url = BINANCE_FUTURES_URL + endpoint

    timestamp = int(time.time() * 1000)
    params = {
        "symbol": symbol,
        "side": side.upper(),
        "type": "MARKET",
        "quantity": quantity,
        "timestamp": timestamp
    }

    query_string = "&".join([f"{key}={params[key]}" for key in params])
    signature = hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature

    headers = {"X-MBX-APIKEY": API_KEY}

    response = requests.post(url, headers=headers, params=params)
    return response.json()

# ✅ 기본 Flask 서버
@app.route('/')
def home():
    return "Flask Server is Running!"

# ✅ Webhook 엔드포인트 (트레이딩뷰 Webhook 요청 처리)
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    symbol = data.get("symbol", "BTCUSDT")
    side = data.get("side", "").upper()
    position_size = float(data.get("position_size", 0))

    if side not in ["BUY", "SELL"]:
        return jsonify({"error": "Invalid order side"}), 400

    # Binance API로 주문 실행
    order_response = place_order(symbol, side, position_size)

    return jsonify(order_response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
