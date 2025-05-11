from flask import Flask, request, jsonify
from utils.response import success, error
from utils.comparables import fetch_property_data, process_comparables_data, compute_average_assessed_value
from utils.refund_service import is_over_assessed, get_years_eligible, calculate_refund
from utils.logger import logger
from dotenv import load_dotenv
import os

load_dotenv()

interest_rates_csv_path = os.getenv("INTEREST_RATES_CSV_PATH", "interest_rates.csv")
app_port = os.getenv("APP_PORT", "5000")

app = Flask(__name__)


@app.route("/")
@app.route("/health")
def default():
    logger.info("Health check endpoint hit.")
    return success(message="Property Tax Refund Estimator Service is running")


@app.route("/refund", methods=["POST"])
def calculate_tax_refund():
    input_data = request.get_json()
    if not input_data or "pin" not in input_data:
        logger.warning("Missing 'pin' in refund request body.")
        return error("Missing 'pin' in request body", status=422)

    pin = input_data["pin"]
    enriched = request.args.get("enriched", "false").lower() == "true"
    logger.info(f"Refund request received for PIN: {pin} with enriched={enriched}")

    data, err, status = fetch_property_data(pin)
    if err:
        logger.error(f"Failed to fetch property data for PIN: {pin} - {err}")
        return error(err, status=status)

    property_, comparables = process_comparables_data(data)
    avg_value = compute_average_assessed_value(comparables)

    sale_date = property_.get("sale date")
    years_eligible = get_years_eligible(sale_date)

    assessed_property_value, is_over_assessed_flag = is_over_assessed(property_, avg_value)
    base_amount = assessed_property_value - avg_value

    if not is_over_assessed_flag or years_eligible == 0:
        logger.info(f"PIN: {pin} is not eligible for refund. Over-assessed: {is_over_assessed_flag}, Years eligible: {years_eligible}")
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
        logger.error(f"Refund calculation error for PIN: {pin} - {refund_error}")
        return error(refund_error, status=500)

    logger.info(f"Refund calculated for PIN: {pin} → ${refund:.2f} over {years_eligible} years")

    response = {
        "pin": pin,
        "yearsEligible": years_eligible,
        "totalRefund": refund
    }

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
        logger.warning("Missing 'pin' in eligibility query param.")
        return error("Missing 'pin' query parameter", status=422)

    logger.info(f"Eligibility check requested for PIN: {pin}")
    data, err, status = fetch_property_data(pin)
    if err:
        logger.error(f"Eligibility check failed for PIN: {pin} - {err}")
        return error(err, status=status)

    property_, comparables = process_comparables_data(data)
    avg_value = compute_average_assessed_value(comparables)

    _, is_over = is_over_assessed(property_, avg_value)
    logger.info(f"Eligibility result for PIN: {pin}, eligible={is_over}")

    message = ""
    if is_over:
        message = "Property is eligible for tax refund"
    else:
        message = "Property assessed value is not greater than average of comparables"
    return success(data={
        "eligible": is_over,
        "propertyAssessedValue": property_.get("assessed value"),
        "averageAssessedValue": avg_value,
    }, message=message)


@app.route("/comparables", methods=["GET"])
def get_comparables():
    pin = request.args.get("pin")
    if not pin:
        logger.warning("Missing 'pin' in comparables query param.")
        return error("Missing 'pin' query parameter in request", status=422)

    logger.info(f"Fetching comparables for PIN: {pin}")
    data, err, status = fetch_property_data(pin)

    if err:
        logger.error(f"Failed to fetch comparables for PIN: {pin} - {err}")
        return error(f"Failed to fetch property data: {err}", status=status)

    property_, comparables = process_comparables_data(data)
    avg_assessed_value = compute_average_assessed_value(comparables)

    return success(data={
        "property": property_,
        "comparableProperties": comparables,
        "averageAssessedValue": avg_assessed_value
    }, message="Fetched comparable properties data successfully")


if __name__ == '__main__':
    logger.info(f"Starting Property Tax Refund Estimator API on port {app_port}")
    app.run(host="0.0.0.0", port=int(app_port))
