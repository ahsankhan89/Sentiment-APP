from flask import Flask, request, render_template, jsonify
from SentimentBot import selenium_code
import sentimentanalysis

app = Flask(__name__, template_folder='templates')

status_message = ""

@app.route("/")
def render_index():
    return render_template('index.html')

@app.route("/automation", methods=['POST'])
def automation():
    global status_message
    if request.method == 'POST':
        search_key = request.form.get('search_key')
        if search_key:
            df = selenium_code(search_key)
            status_message = "Initiating Sentiment Analysis"
            sentimentanalysis.do_analysis(df)
            return jsonify(status='Sentiment Done')

@app.route("/status", methods=['GET'])
def get_status():
    global status_message
    return jsonify({"message": status_message})

@app.route("/update_status", methods=['POST'])
def update_status():
    global status_message
    status_message = request.json['status']
    return jsonify({"message": "Status updated"})

if __name__ == "__main__":
    app.run(debug=True, port=1000)