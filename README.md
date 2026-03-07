# ACEest Fitness & Gym — DevOps CI/CD Pipeline

> **M.Tech Software Engineering | Introduction to DevOps (CSIZG514/SEZG514/SEUSZG514)**
> Assignment 1 — Implementing Automated CI/CD Pipelines

---

## 📋 Project Overview

This project demonstrates a complete DevOps workflow for the **ACEest Fitness & Gym** application — a Flask-based REST API converted from a Tkinter desktop application. It showcases industry-standard practices including Version Control, Containerization, and automated CI/CD pipelines via **GitHub Actions** and **Jenkins**.

---

## 🏗️ Project Structure

```
aceest-devops-assignment/
├── app.py                        # Flask REST API (core application)
├── test_app.py                   # Pytest unit test suite
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Multi-stage Docker image
├── Jenkinsfile                   # Jenkins declarative pipeline
├── .github/
│   └── workflows/
│       └── main.yml              # GitHub Actions CI/CD workflow
└── README.md                     # This file
```

---

## 🚀 Local Setup & Execution

### Prerequisites
- Python 3.11+
- Docker Desktop
- Git

### Step 1 — Clone the repository
```bash
git clone https://github.com/<your-username>/aceest-devops-assignment.git
cd aceest-devops-assignment
```

### Step 2 — Create a virtual environment and install dependencies
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Step 3 — Run the Flask application locally
```bash
python app.py
```
The API will be available at `http://localhost:5000`

### Step 4 — Test the API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info & endpoint list |
| GET | `/health` | Health check |
| GET | `/programs` | All fitness programs |
| GET | `/programs/FL` | Fat Loss program details |
| GET | `/programs/MG` | Muscle Gain program details |
| GET | `/programs/BG` | Beginner program details |
| GET | `/calories/FL/75.0` | Calorie estimate (75kg, Fat Loss) |
| POST | `/members` | Register a new member |
| GET | `/members` | List all members |

#### Example POST request:
```bash
curl -X POST http://localhost:5000/members \
  -H "Content-Type: application/json" \
  -d '{"name": "Arjun Kumar", "age": 28, "weight_kg": 75.0, "program": "FL"}'
```

---

## 🧪 Running Tests Manually

### Run all tests
```bash
pytest test_app.py -v
```

### Run with coverage report
```bash
pytest test_app.py -v --cov=app --cov-report=term-missing
```

### Run a specific test class
```bash
pytest test_app.py::TestPrograms -v
pytest test_app.py::TestMembers -v
```

The test suite includes **40+ test cases** covering:
- Home & health check endpoints
- All program retrieval (full name and short code)
- Calorie calculation logic and edge cases
- Member registration, validation, and conflict handling
- Error handling (400, 404, 409 responses)

---

## 🐳 Docker Usage

### Build the Docker image
```bash
docker build -t aceest-fitness:latest .
```

### Run the containerized application
```bash
docker run -p 5000:5000 aceest-fitness:latest
```

### Run tests inside the container
```bash
docker run --rm \
  -v $(pwd)/test_app.py:/app/test_app.py \
  --entrypoint pytest \
  aceest-fitness:latest \
  test_app.py -v
```

### Check container health
```bash
docker ps   # Shows health status after ~30s
```

The `Dockerfile` uses a **multi-stage build** to keep the final image small and runs the application as a **non-root user** for security.

---

## ⚙️ GitHub Actions CI/CD Integration

**File:** `.github/workflows/main.yml`

The pipeline is triggered automatically on every `push` and `pull_request`. It runs 4 sequential stages:

```
[Push to GitHub]
       │
       ▼
┌─────────────────┐
│ Stage 1: Lint   │  flake8 checks app.py and test_app.py for syntax errors
└────────┬────────┘
         │ (passes)
         ▼
┌──────────────────────┐
│ Stage 2: Docker Build│  Builds Docker image, saves as pipeline artifact
└──────────┬───────────┘
           │ (passes)
           ▼
┌────────────────────────────┐
│ Stage 3: Automated Testing │  Loads image, runs pytest inside the container
└──────────────┬─────────────┘
               │ (all pass)
               ▼
┌──────────────────────┐
│ Stage 4: Summary ✅  │  Prints build summary with commit SHA and branch
└──────────────────────┘
```

**Key design decisions:**
- Each stage `needs:` the previous stage — a lint failure stops the pipeline immediately
- The Docker image is saved as a GitHub Actions **artifact** and reused in the test stage (no redundant builds)
- Tests run **inside the container** to validate the final deployable artifact, not just the source code

---

## 🔧 Jenkins BUILD Integration

**File:** `Jenkinsfile`

Jenkins is configured as a secondary build layer. It validates code in a controlled server environment independent of GitHub Actions.

### Jenkins Setup Steps

1. **Install Jenkins** (locally or on a server):
   ```bash
   # Using Docker (easiest):
   docker run -p 8080:8080 -p 50000:50000 \
     -v jenkins_home:/var/jenkins_home \
     jenkins/jenkins:lts
   ```
   Then open `http://localhost:8080` and complete the setup wizard.

2. **Install required Jenkins plugins:**
   - Git plugin
   - Pipeline plugin
   - JUnit plugin

3. **Create a new Pipeline project:**
   - Click **New Item** → name it `aceest-fitness` → select **Pipeline** → OK
   - Under **Pipeline**, set Definition to **Pipeline script from SCM**
   - Set SCM to **Git** and enter your GitHub repo URL
   - Set Script Path to `Jenkinsfile`
   - Save and click **Build Now**

### Jenkins Pipeline Stages

| Stage | Description |
|-------|-------------|
| Checkout | Pulls latest code from GitHub |
| Environment Setup | Creates Python venv, installs requirements |
| Lint | Runs flake8 on source files |
| Unit Tests | Runs pytest, publishes JUnit XML report |
| Docker Build | Builds Docker image tagged with build number |
| Docker Test | Runs pytest inside the built container |

---

## 📊 Version Control Strategy

This project follows a structured Git branching and commit strategy:

| Branch | Purpose |
|--------|---------|
| `main` | Stable, production-ready code |
| `feature/*` | New features |
| `fix/*` | Bug fixes |
| `infra/*` | CI/CD and Docker changes |

**Commit message format:**
```
feat: add calorie calculation endpoint
fix: handle empty member name validation
infra: add multi-stage Dockerfile
test: add edge case tests for member registration
docs: update README with Jenkins setup steps
```

---

## 🎓 Technologies Used

| Technology | Role |
|------------|------|
| Python / Flask | Web application framework |
| Pytest | Unit testing framework |
| Git / GitHub | Version control |
| Docker | Containerization (multi-stage build) |
| GitHub Actions | Automated CI/CD pipeline |
| Jenkins | Secondary BUILD server |
| flake8 | Python linting |