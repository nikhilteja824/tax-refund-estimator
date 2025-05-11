from datetime import datetime
import pandas as pd
from utils.logger import logger

MAX_ELIGIBLE_YEARS = 4


def calculate_refund(base_amount, years_eligible, interest_csv_path):
    """
    Computes the total refund adjusted to present value using compound interest rates.
    Source of Truth for Refund calculation: API Contract provided
    Returns (total_refund: float, error_message: str, refund_breakdown: dict)
    """
    logger.info(f"Starting refund calculation for base amount: {base_amount}, years eligible: {years_eligible}")

    if base_amount <= 0 or years_eligible == 0:
        logger.warning("Base amount <= 0 or no eligible years — refund will be zero")
        return 0.0, None, {}

    try:
        rates_df = pd.read_csv(interest_csv_path)
        rates_df.columns = [col.lower() for col in rates_df.columns]
        logger.info(f"Loaded interest rate CSV from {interest_csv_path}")

        if "year" not in rates_df.columns or "rate" not in rates_df.columns:
            logger.error("Interest CSV missing 'year' or 'rate' column")
            return None, "Can't compute tax refund due to invalid interest rate config", {}

        rates_df = rates_df.dropna(subset=["year"])

        rates = {}
        for _, row in rates_df.iterrows():
            year = row["year"]
            rate = row["rate"]

            try:
                year = int(year)
                if pd.isna(rate) or rate == "":
                    raise ValueError
                rate = float(rate)
            except (ValueError, TypeError):
                logger.warning(f"Skipping invalid rate entry: year={row['year']}, rate={row['rate']}")
                return None, "Can't compute tax refund due to invalid interest rate config", {}

            rates[year] = rate

        current_year = datetime.today().year
        last_full_year = current_year - 1

        total_refund = 0.0
        refund_breakdown = {}

        for y in range(last_full_year, last_full_year - years_eligible, -1):
            compound = 1.0
            for n in range(y, last_full_year + 1):
                rate = rates.get(n)
                if rate is None:
                    logger.error(f"Missing interest rate for year {n}")
                    raise ValueError
                compound *= (1 + rate)

            year_refund = base_amount * compound
            refund_breakdown[str(y)] = round(year_refund, 2)
            total_refund += year_refund

        logger.info(f"Refund calculation completed: Total refund = {total_refund}")
        return round(total_refund, 2), None, refund_breakdown

    except Exception as e:
        logger.exception("Unexpected error during refund calculation")
        return None, "Can't compute tax refund due to invalid interest rate config", {}


def is_over_assessed(property_, avg_assessed_value):
    """
    Returns a tuple: (assessed_value: float, is_over_assessed: bool)
    """
    property_assessed_value = property_.get("assessed value")

    if property_assessed_value is None or avg_assessed_value is None:
        logger.warning("Missing values for over-assessment check")
        return None, False

    result = property_assessed_value > avg_assessed_value
    logger.info(f"Over-assessment check: assessed={property_assessed_value}, average={avg_assessed_value}, over_assessed={result}")
    return property_assessed_value, result


def get_years_eligible(sale_date_str, max_years=MAX_ELIGIBLE_YEARS):
    """
    Considers only the full calendar years for eligibility of ownership.
    Caps at max_years (currently set as 4).
    """
    if not sale_date_str:
        logger.warning("No sale date provided")
        return 0

    try:
        sale_date = datetime.strptime(sale_date_str, "%m/%d/%Y")
        current_year = datetime.today().year

        first_eligible_year = sale_date.year + 1
        if sale_date.month == 1 and sale_date.day == 1:
            first_eligible_year = sale_date.year

        last_full_year = current_year - 1
        eligible_years = max(0, last_full_year - first_eligible_year + 1)
        valid_years = min(eligible_years, max_years)

        logger.info(f"Calculated eligible years: {valid_years} (from sale date: {sale_date_str})")
        return valid_years

    except ValueError:
        logger.warning(f"Invalid sale date format received: {sale_date_str}")
        return 0
