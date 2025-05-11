# Property Tax Refund Estimator


## Overview



This is a containerized Python-Flask microservice for estimating property tax refunds by analyzing assessed values and comparable properties.


Features:
- Computes refund based on assessed value vs comparable properties
- Adjusts refund using compound interest rates from the past 4 years
- Uses an internal Comparables API to fetch property data like:
  - Assessed values
  - Sale dates
  - Similar nearby properties


It provides a REST API endpoint `/refund` that:

- Accepts a property PIN
- Fetches assessment data from the Comparables API
- Calculates average assessed value of comparable properties
- Determines over-assessment and eligible years (up to 4)
- Computes refund for each year and adjusts to present-day value using `interest_rates.csv`



## Steps to Build & Run 

1. Clone the repository
````markdown
git clone https://github.com/your-username/tax-refund-estimator.git
cd tax-refund-estimator
````


2. Add Environment variables section
````markdown
COMPARABLES_API_HOST= {host}
COMPARABLES_API_PORT= {port}

#Optional
INTEREST_RATES_CSV_PATH=interest_rates.csv
APP_PORT=5000
````

3. Build the docker image 
````markdown
docker build -t tax-refund-estimator .
````

4. Run the Container
````markdown
docker run --env-file .env -p 5000:5000 tax-refund-estimator
docker run -d --env-file .env -p 5000:5000 tax-refund-estimator (for detached mode)
````

5. Now the api's are exposed at  http://localhost:5000

6. Follow the endpoints listed below based on use case

7. Logs are available for the service in files service.log and service-error.log
````markdown
service.log — contains all logs at level INFO or above
service-error.log — contains only logs at level ERROR or above
````

8. Automated tests for all important validations are available in tests/ directory. To run them
````markdown
pytest tests/
````


## Sample Request and cURL

**POST** `/refund`  
```json
{
  "pin": "26062070090000"
}
```

````markdown
curl --location 'http://127.0.0.1:5000/refund' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--data '{
    "pin" : 26062070090000
}'
````


## Sample Response
```json
{
  "pin": "26062070090000",
  "yearsEligible": 4,
  "totalRefund": 7043.40
}
```


## Enhancements done
These are over and beyond the scope of API contract provided.
  - Some of these are useful for user facing side and others for tech debugging and usage

1. Eligibility API endpoint
    - Quickly checks if a property is over-assessed and potentially eligible for a refund.

2. Comparables Wrapper API endpoint
    - Helps debug refund issues by exposing the actual comparables and average calculation used internally.

3. Enriched refund mode
    - An optional ?enriched=true query param gives:
    - Refund breakdown by year
    - Property summary context
    - This avoids bloating the base response but provides insights when needed.

4. Structured Logging
    - Logs added across all important control paths
    - Useful for debugging both user errors (4xx) and system failures (5xx)
    - Logs are separated cleanly into general and error files

## All Endpoints Available
curl commands for all endpoints are mentioned in api_endpoints.md file in the root directory

| Method | Endpoint                 | Description                                                  |
|--------|--------------------------|--------------------------------------------------------------|
| GET    | `/health`                | Health check for the service                                 |
| POST   | `/refund`                | Calculates total refund based on assessed value              |
| POST   | `/refund?enriched=true`  | Same as `/refund` but includes breakdown and property summary |
| GET    | `/eligibility?pin=...`   | Checks if a property is eligible for a refund                |
| GET    | `/comparables?pin=...`   | Returns property data, comparables, and average assessed value |


## Some thoughts that i had on what else can be done

Currently, this microservice alone can't include these fields as it needs web scraping from public website 
https://cookcountyassessor.com/pin/{pin}
(ideally exposed by Comparables API to avoid scraping from multiple services)
1. Adding a field NextAssessementYear:
    - Because this is important field that can help know when a reassessment can reset their refund window

2. An important parameter assessment_ratio:
    - assessment_ratio = subject_assessed_value / subject_market_value
    - Indicates how inflated (or deflated) the tax authority’s valuation is compared to the actual market.













