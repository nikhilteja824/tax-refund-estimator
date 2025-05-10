from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/")
@app.route("/health")
def default():
    return jsonify({
        "message" : "Property Tax Refund Serivce is running"
    }), 200


# Just a placeholder for now to verify service is coming up
@app.route("/refund", methods = ['POST'])
def calculate_refund():

    input_data = request.get_json()
    return jsonify({
        "message" : "API hit successful for calculating tax refund"
    }), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port= 5000)