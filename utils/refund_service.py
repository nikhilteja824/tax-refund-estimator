from datetime import datetime
import pandas as pd

MAX_ELIGIBLE_YEARS = 4

def calculate_refund(base_amount, years_eligible, interest_csv_path):
    """
    Computes the total refund adjusted to present value using compound interest rates.
    Source of Truth for Refund calculation: API Contract provided
    Returns (total_refund: float, error_message: str )
    """
    if base_amount <= 0 or years_eligible == 0:
        return 0.0, None

    try:
        rates_df = pd.read_csv(interest_csv_path)
        rates_df.columns = [col.lower() for col in rates_df.columns]

        if "year" not in rates_df.columns or "rate" not in rates_df.columns:
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
                    raise ValueError
                compound *= (1 + rate)
            year_refund = base_amount * compound
            refund_breakdown[str(y)] = round(year_refund, 2)
            total_refund += year_refund

        return round(total_refund, 2), None, refund_breakdown


    except Exception:
        return None, "Can't compute tax refund due to invalid interest rate config", {}



def is_over_assessed(property_, avg_assessed_value):
    """
    Returns a tuple: (assessed_value: float, is_over_assessed: bool)
    """
    property_assessed_value = property_.get("assessed value")

    # If either value is missing, we can't make a decision
    if property_assessed_value is None or avg_assessed_value is None:
        return None, False

    return property_assessed_value, property_assessed_value > avg_assessed_value



def get_years_eligible(sale_date_str, max_years=MAX_ELIGIBLE_YEARS):
    """
    Considers only the full calendar years for eligibility of ownership
    Caps at max_years (currently set as 4).
    """
    if not sale_date_str:
        return 0

    try:
        sale_date = datetime.strptime(sale_date_str, "%m/%d/%Y")
        current_year = datetime.today().year


        first_eligible_year = sale_date.year + 1
        # Considering Sale on Jan 1st of an year makes it eligible for Full calendar year
        if sale_date.month == 1 and sale_date.day == 1:
            first_eligible_year = sale_date.year

        last_full_year = current_year - 1
        eligible_years = max(0, last_full_year - first_eligible_year + 1)
        return min(eligible_years, max_years)
    
    # To handle if we get any invalid date format
    except ValueError:
        return 0  

