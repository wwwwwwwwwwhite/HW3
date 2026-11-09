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

## Run with Docker Compose

Install Docker Desktop, then set the Docker Hub username in your shell:

```bash
export DOCKERHUB_USERNAME=your-dockerhub-username
docker compose up -d --build
docker compose ps
```

Compose publishes port 8000, uses the `unless-stopped` restart policy, and checks `/health`. To stop the service, run `docker compose down`.

## CI/CD architecture

`.github/workflows/ci-cd.yml` runs pytest on pull requests and pushes to `main`. Pull requests stop after tests: they do not publish or deploy. A successful push to `main` builds and pushes `linux/amd64` and `linux/arm64` images to Docker Hub with both `latest` and the full Git commit SHA tags. The publish job depends on the test job, so a failed test blocks release.

Add these repository Actions secrets before enabling release:

- `DOCKERHUB_USERNAME`: Docker Hub account name.
- `DOCKERHUB_TOKEN`: Docker Hub access token (not the account password).

Deployment then runs on a self-hosted macOS ARM64 GitHub Actions runner. Install and start the GitHub runner on the Mac that has Docker Desktop available, and add the `self-hosted`, `macOS`, and `ARM64` labels. The deploy job only runs after a successful `main` image publish. It logs in to Docker Hub, pulls the exact commit-SHA image with Docker Compose, recreates the service, and fails unless both the container is running and `http://127.0.0.1:8000/health` responds successfully.

The workflow does not install or register a runner, configure GitHub secrets, or grant access to Docker Hub. Complete those account- and machine-specific setup steps in GitHub and Docker Desktop before expecting a hosted deployment.
