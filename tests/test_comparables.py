import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.comparables import compute_average_assessed_value, process_comparables_data

def test_compute_average_assessed_value():
    comparables = [
        {"assessed value": 27000},
        {"assessed value": 29000},
        {"assessed value": 31000}
    ]
    avg = compute_average_assessed_value(comparables)
    assert avg == 29000

def test_process_comparables_data():
    mock_data = {
        "prop1": {"assessed value": 30000},
        "prop2": {"assessed value": 31000},
        "prop3": {"assessed value": 32000}
    }
    property_, comparables = process_comparables_data(mock_data)
    assert property_ == mock_data["prop1"]
    assert len(comparables) == 2
    assert comparables[0]["assessed value"] == 31000