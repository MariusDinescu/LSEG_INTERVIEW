from flask import Flask, render_template, request, jsonify, session
import json, os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load JSON file
with open('stock_data.json') as f:
    stock_data = json.load(f)

@app.route('/')
def index():
    session.clear()
    return render_template('index.html', message="Hello! Welcome to LSEG. I'm here to help you.", exchanges=list(stock_data.keys()))

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('user_input')
    state = session.get('state', 'start')
    selected_exchange = session.get('selected_exchange')
    selected_stock = session.get('selected_stock')

    # Select stock exchange
    if state == 'start':
        if user_input in stock_data:
            session['selected_exchange'] = user_input
            session['state'] = 'stock_selection'
            options = [stock['name'] for stock in stock_data[user_input]]
            return jsonify({'bot': f"You selected {user_input}. Please select a stock:", 'options': options})
        else:
            return jsonify({'bot': "Invalid exchange. Please select one of the listed exchanges."})

    # Select stock
    elif state == 'stock_selection':
        for stock in stock_data[selected_exchange]:
            if stock['name'] == user_input:
                session['selected_stock'] = user_input
                session['state'] = 'final'
                return jsonify({
                    'bot': f"Stock Price of {stock['name']} is ${stock['price']}.",
                    'options': ["Main menu", "Go Back"]
                })
        return jsonify({'bot': "Invalid stock. Please select one from the list."})

    # Final options
    elif state == 'final':
        if user_input == "Main menu":
            session.clear()
            return jsonify({'bot': "Back to main menu. Please select a Stock Exchange.", 'options': list(stock_data.keys())})
        elif user_input == "Go Back":
            session['state'] = 'stock_selection'
            options = [stock['name'] for stock in stock_data[selected_exchange]]
            return jsonify({'bot': "Please select a stock:", 'options': options})
        else:
            return jsonify({'bot': "Invalid option. Please select Main menu or Go Back."})

    return jsonify({'bot': "Something went wrong. Please try again."})

if __name__ == '__main__':
    app.run(debug=True)
