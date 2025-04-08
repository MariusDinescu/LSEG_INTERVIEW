from flask import Flask, render_template, request, jsonify, session
import json, os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# load JSON file
with open('stock.json') as f:
    stock_data = json.load(f)

@app.route('/')
def index():
    session.clear()
    exchanges = [exchange['stockExchange'] for exchange in stock_data]
    return render_template('index.html', message="Hello! Welcome to LSEG. I'm here to help you.", exchanges=exchanges)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('user_input')
    state = session.get('state', 'start')
    selected_exchange = session.get('selected_exchange')
    selected_stock = session.get('selected_stock')

    # select stock exchange
    if state == 'start':
        exchange = next((ex for ex in stock_data if ex['stockExchange'] == user_input), None)
        if exchange:
            session['selected_exchange'] = user_input
            session['state'] = 'stock_selection'
            options = [stock['stockName'] for stock in exchange['topStocks']]
            return jsonify({'bot': f"You selected {user_input}. Please select a stock:", 'options': options})
        else:
            return jsonify({'bot': "Invalid exchange. Please select one of the listed exchanges."})

    # select stock
    elif state == 'stock_selection':
        exchange = next((ex for ex in stock_data if ex['stockExchange'] == selected_exchange), None)
        for stock in exchange['topStocks']:
            if stock['stockName'] == user_input:
                session['selected_stock'] = user_input
                session['state'] = 'final'
                return jsonify({
                    'bot': f"Stock Price of {stock['stockName']} is {stock['price']}.",
                    'options': ["Main menu", "Go Back"]
                })
        return jsonify({'bot': "Invalid stock. Please select one from the list."})

    # final options
    elif state == 'final':
        if user_input == "Main menu":
            session.clear()
            return jsonify({'bot': "Back to main menu. Please select a Stock Exchange.", 'options': [ex['stockExchange'] for ex in stock_data]})
        elif user_input == "Go Back":
            session['state'] = 'stock_selection'
            exchange = next((ex for ex in stock_data if ex['stockExchange'] == selected_exchange), None)
            options = [stock['stockName'] for stock in exchange['topStocks']]
            return jsonify({'bot': "Please select a stock:", 'options': options})
        else:
            return jsonify({'bot': "Invalid option. Please select Main menu or Go Back."})

    return jsonify({'bot': "Something went wrong. Please try again."})

if __name__ == '__main__':
    app.run(debug=True)