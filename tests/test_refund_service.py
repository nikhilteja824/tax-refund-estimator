import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.refund_service import calculate_refund, is_over_assessed, get_years_eligible

# Creating a temp csv file with data manipulation to support testing
def test_calculate_refund_success(tmp_path):
    csv_path = tmp_path / "interest_rates.csv"
    df = pd.DataFrame({
        "Year": [2021, 2022, 2023, 2024],
        "Rate": [0.01, 0.015, 0.02, 0.025]
    })
    df.to_csv(csv_path, index=False)

    base_amount = 1000
    years_eligible = 3
    refund, error, refund_breakdown = calculate_refund(base_amount, years_eligible, str(csv_path))

    assert error is None
    assert refund == 3131.68
    assert refund_breakdown is not None


def test_calculate_refund_missing_year(tmp_path):
    # CSV missing 2023
    csv_path = tmp_path / "interest_rates.csv"
    df = pd.DataFrame({
        "Year": [2021, 2022, 2024],
        "Rate": [0.01, 0.015, 0.025]
    })
    df.to_csv(csv_path, index=False)

    base_amount = 1000
    years_eligible = 3
    refund, error, refund_breakdown = calculate_refund(base_amount, years_eligible, str(csv_path))

    assert refund is None
    assert error is not None
    assert refund_breakdown == {}


def test_calculate_refund_invalid_rate(tmp_path):
    csv_path = tmp_path / "interest_rates.csv"
    df = pd.DataFrame({
        "Year": [2021, 2022, 2023],
        "Rate": [0.01, "abc", 0.025]
    })
    df.to_csv(csv_path, index=False)

    refund, error, refund_breakdown = calculate_refund(1000, 3, str(csv_path))
    assert refund is None
    assert error is not None
    assert refund_breakdown == {}


def test_is_over_assessed_success():
    property_ = {"assessed value": 35000}
    avg = 30000
    value, flag = is_over_assessed(property_, avg)
    assert value == 35000
    assert flag is True

def test_is_over_assessed_failure():
    property_ = {"assessed value": 28000}
    avg = 30000
    value, flag = is_over_assessed(property_, avg)
    assert value == 28000
    assert flag is False


def test_get_years_eligible_success():
    years = get_years_eligible("1/1/2020", max_years=4)
    assert years == 4

def test_get_years_eligible_failure():
    years = get_years_eligible("invalid-date", max_years=4)
    assert years == 0