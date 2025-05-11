# API Usage Examples with cURL

This document contains sample `curl` commands for testing the available API endpoints. Please see the notes below before running.

---

## Health Check

```bash
curl http://localhost:5000/health
```

---

## Refund Calculation

```bash
curl -X POST http://localhost:5000/refund \
  -H "Content-Type: application/json" \
  -d '{"pin": "26062070090000"}'
```

---

## Enriched Refund Calculation

```bash
curl -X POST "http://localhost:5000/refund?enriched=true" \
  -H "Content-Type: application/json" \
  -d '{"pin": "26062070090000"}'
```

---

## Eligibility Check

```bash
curl "http://localhost:5000/eligibility?pin=26062070090000"
```

---

## Comparables Data

```bash
curl "http://localhost:5000/comparables?pin=26062070090000"
```

---

## Notes

- Replace `26062070090000` with any valid PIN.
- These commands assume the container is running locally and port 5000 is exposed.
- Enriched mode is optional and adds additional data like refund breakdown and property summary.
