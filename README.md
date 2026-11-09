# BuildMyPC

BuildMyPC is a Korean-language PC configuration recommender. Enter a budget, use case, preferred resolution, CPU/GPU brands, memory, and storage to receive a parts list with reference prices and compatibility checks.

The product catalog in `app/data/products.json` is manually maintained demo data, not live pricing or inventory. Check current prices, availability, and compatibility with vendors before purchasing.

## Run locally

Requirements: Python 3.12 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000>. The health endpoint is <http://127.0.0.1:8000/health>.

Run tests:

```bash
python -m pytest -q
```

## CI

`.github/workflows/ci.yml` runs pytest on pull requests and pushes to `main`. It only installs the Python dependencies and runs the test suite; image publishing and deployment are not configured.
