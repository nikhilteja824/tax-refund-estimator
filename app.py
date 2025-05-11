from flask import Flask, request, jsonify
from utils.response import success, error
from utils.comparables import fetch_property_data, process_comparables_data, compute_average_assessed_value
from utils.refund_service import is_over_assessed, get_years_eligible, calculate_refund
from dotenv import load_dotenv
import os

load_dotenv()

interest_rates_csv_path = os.getenv("INTEREST_RATES_CSV_PATH", "interest_rates.csv")
app_port = os.getenv("APP_PORT", "5000")

app = Flask(__name__)


@app.route("/")
@app.route("/health")
def default():
    return success(message="Property Tax Refund Estimator Service is running")


@app.route("/refund", methods=["POST"])
def calculate_tax_refund():
    input_data = request.get_json()
    if not input_data or "pin" not in input_data:
        return error("Missing 'pin' in request body", status=422)

    pin = input_data["pin"]
    enriched = request.args.get("enriched", "false").lower() == "true"

    data, err, status = fetch_property_data(pin)
    if err:
        return error(err, status=status)

    property_, comparables = process_comparables_data(data)
    avg_value = compute_average_assessed_value(comparables)


    sale_date = property_.get("sale date")
    years_eligible = get_years_eligible(sale_date)

    

    assessed_property_value, is_over_assessed_flag = is_over_assessed(property_, avg_value)
    base_amount = assessed_property_value - avg_value
    if not is_over_assessed_flag or years_eligible == 0:
        return success(data={
            "pin": pin,
            "yearsEligible": 0,
            "totalRefund": 0.0,
        })

    
    refund, refund_error, refund_breakdown = calculate_refund(
        base_amount=base_amount,
        years_eligible=years_eligible,
        interest_csv_path=interest_rates_csv_path
    )

    if refund_error:
        return error(refund_error, status=500)
    
    response = {
        "pin": pin,
        "yearsEligible": years_eligible,
        "totalRefund": refund
    }

    # These are optional response data fields based on enriched flag in query parameters
    if enriched:
        response["taxRefundBreakdown"] = refund_breakdown
        response["propertySummary"] = {
            "address": property_.get("address"),
            "class": property_.get("class"),
            "saleDate": property_.get("sale date"),
            "propertyAssessedValue": assessed_property_value
        }

    return success(data=response)


@app.route("/eligibility", methods=["GET"])
def check_eligibility_for_refund():
    pin = request.args.get("pin")
    if not pin:
        return error("Missing 'pin' query parameter", status=422)

    data, err, status = fetch_property_data(pin)
    if err:
        return error(err, status=status)

    property_, comparables = process_comparables_data(data)
    avg_value = compute_average_assessed_value(comparables)

    _, is_over = is_over_assessed(property_, avg_value)
    if not is_over:
        return success(data={
            "eligible": False,
            "propertyAssessedValue": property_.get("assessed value"),
            "averageAssessedValue": avg_value,
        }, message="Property assessed value is not greater than average of comparables")

    return success(data={
        "eligible": True,
        "propertyAssessedValue": property_.get("assessed value"),
        "averageAssessedValue": avg_value,
    }, message="Property is eligible for tax refund")


@app.route("/comparables", methods=["GET"])
def get_comparables():
    pin = request.args.get("pin")
    if not pin:
        return error("Missing 'pin' query parameter in request", status=422)
    
    # We get three fields from comparables module
    data, err, status = fetch_property_data(pin)

    if err:
        return error(f"Failed to fetch property data: {err}", status=status)
    property_, comparables = process_comparables_data(data)
    avg_assessed_value = compute_average_assessed_value(comparables)

    
    return success(data={
        "property" : property_,
        "comparableProperties" : comparables,
        "averageAssessedValue" : avg_assessed_value

    }, message="Fetched comparable properties data successfully")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port= app_port, debug=True)