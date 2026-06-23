"""Flask 웹 대시보드"""

from flask import Flask, render_template, jsonify, request
from inventory import (
    calc_cost, sell, check_low_stock, get_stock_summary,
    restock, get_sales_summary, load_stock
)
from notifier import notify_low_stock
from data import RECIPES

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/stock")
def api_stock():
    return jsonify(get_stock_summary())


@app.route("/api/costs")
def api_costs():
    stock = load_stock()
    return jsonify({name: calc_cost(name, stock) for name in RECIPES})


@app.route("/api/sales")
def api_sales():
    return jsonify(get_sales_summary())


@app.route("/api/sell", methods=["POST"])
def api_sell():
    data = request.get_json()
    menu = data.get("menu", "")
    qty = int(data.get("qty", 1))
    try:
        result = sell(menu, qty)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/restock", methods=["POST"])
def api_restock():
    data = request.get_json()
    ingredient = data.get("ingredient", "")
    amount = float(data.get("amount", 0))
    try:
        restock(ingredient, amount)
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/order", methods=["POST"])
def api_order():
    low = check_low_stock()
    if not low:
        return jsonify({"sent": False, "message": "재고 부족 없음"})
    results = notify_low_stock(low)
    return jsonify({"sent": True, "categories": list(results.keys())})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
