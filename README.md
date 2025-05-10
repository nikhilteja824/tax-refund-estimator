# Property Tax Refund Estimator


## Overview



This is a containerized Python-Flask microservice for estimating property tax refunds based on over-assessment.


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



## Sample Request and cURL

**POST** `/refund`  
```json
{
  "pin": "26062070090000"
}
```


## Sample Response
```json
{
  "pin": "26062070090000",
  "yearsEligible": 4,
  "totalRefund": 7043.40
}
```



