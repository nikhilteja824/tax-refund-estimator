from flask import Flask, request, jsonify
from utils.response import success, error
from utils.comparables import fetch_property_data, process_comparables_data, compute_average_assessed_value

app = Flask(__name__)


@app.route("/")
@app.route("/health")
def default():
    return success(message="Property Tax Refund Estimator Service is running")


# Just a placeholder for now to verify service is coming up
@app.route("/refund", methods = ['POST'])
def calculate_refund():

    input_data = request.get_json()
    if not input_data or "pin" not in input_data:
        return error("Missing 'pin' in request body", status=422)
    return success(data={"input": input_data}, message="Refund endpoint hit success")



@app.route("/comparables", methods=["GET"])
def get_comparables():
    pin = request.args.get("pin")
    if not pin:
        return error("Missing 'pin' query parameter in request", status=422)
    
    # We get three fields from comparables module
    data, err, status = fetch_property_data(pin)
    subject, comparables = process_comparables_data(data)
    avg_assessed_val = compute_average_assessed_value(comparables)
    if err:
        return error(f"Failed to fetch property data: {err}", status=status)
    
    return success(data={
        "subject_property" : subject,
        "comparable_properties" : comparables,
        "average_assessed_value" : avg_assessed_val

    }, message="Fetched comparable properties data successfully")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port= 5000, debug=True)