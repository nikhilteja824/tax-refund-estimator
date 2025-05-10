from flask import Flask, request, jsonify
from utils.response import success, error

app = Flask(__name__)


@app.route("/")
@app.route("/health")
def default():
    return success(message="Property Tax Refund Estimator API is running")


# Just a placeholder for now to verify service is coming up
@app.route("/refund", methods = ['POST'])
def calculate_refund():

    input_data = request.get_json()
    if not input_data or "pin" not in input_data:
        return error("Missing 'pin' in request body", status=422)
    return success(data={"input": input_data}, message="Refund endpoint hit success")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port= 5000, debug=True)