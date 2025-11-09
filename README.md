# selenium-login-automation

A complete Selenium WebDriver test automation project using Python, PyTest, and Page Object Model (POM) to validate login and logout functionality. Includes HTML reporting, screenshots on failures, dotenv-based configuration, and a GitHub Actions CI workflow.

## Features
- Page Object Model under `src/pages/`
- PyTest test suite under `src/tests/`
- HTML report via `pytest-html`
- Screenshots on failures stored in `screenshots/`
- Config via `.env` under `src/config/`
- Headless/Headed runs with `--headless` flag
- GitHub Actions CI generating and uploading HTML report

## Project Structure
```
selenium-login-automation/
├─ .gitignore
├─ README.md
├─ requirements.txt
├─ pytest.ini
├─ .github/workflows/ci.yml
├─ src/
│  ├─ config/
│  │  └─ .env.example
│  ├─ pages/
│  │  ├─ __init__.py
│  │  ├─ base_page.py
│  │  └─ login_page.py
│  ├─ utils/
│  │  ├─ __init__.py
│  │  ├─ driver_factory.py
│  │  └─ logger.py
│  └─ tests/
│     ├─ __init__.py
│     ├─ conftest.py
│     └─ test_login_logout.py
├─ reports/        # HTML reports (created at runtime)
└─ screenshots/    # Failure screenshots (created at runtime)
```

## Prerequisites
- Python 3.10+
- Google Chrome (or Chromium)
- ChromeDriver available on PATH (version compatible with Chrome)

### Install ChromeDriver
You must have ChromeDriver on your PATH. Options:

- Ubuntu/Debian:
  ```bash
  sudo apt-get update
  sudo apt-get install -y chromium-browser chromium-chromedriver || true
  # Or use separate packages depending on distro
  which chromedriver
  chromedriver --version
  ```

- macOS (Homebrew):
  ```bash
  brew install --cask google-chrome
  brew install chromedriver
  which chromedriver
  chromedriver --version
  ```

- Windows:
  - Install Google Chrome.
  - Download ChromeDriver from: https://googlechromelabs.github.io/chrome-for-testing/
  - Extract and add the folder containing `chromedriver.exe` to your PATH.

## Setup
1. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp src/config/.env.example src/config/.env
   # Edit src/config/.env and set your values
   ```
   `.env` keys:
   - `BASE_URL` – login page URL for the target application
   - `VALID_USERNAME` – valid username for login
   - `VALID_PASSWORD` – valid password for login

4. Update locators in `src/pages/login_page.py` to match your site.

## Running Tests Locally
- Headless (recommended for CI):
  ```bash
  pytest -q --headless --html=reports/report.html --self-contained-html
  ```

- Parallel run (uses all CPUs) with headless:
  ```bash
  pytest -n auto -q --headless --html=reports/report.html --self-contained-html
  ```

- Headed (visible browser window):
  ```bash
  pytest -q --html=reports/report.html --self-contained-html
  ```

Reports will be created under `reports/report.html`. Screenshots for failing tests are placed under `screenshots/` with a timestamped filename.

Note: Tests are skipped by default if `BASE_URL` is left as `https://example.com/login`. Set `BASE_URL` and fix locators to enable execution.

## CI with GitHub Actions
- Workflow file: `.github/workflows/ci.yml`
- Triggers on push and pull request to `main`.
- Sets up Python 3.10, installs Chrome and ChromeDriver.
- Installs dependencies and runs PyTest in headless mode.
- Generates self-contained HTML report at `reports/report.html` and uploads it as an artifact.

You can also configure repository secrets (`BASE_URL`, `VALID_USERNAME`, `VALID_PASSWORD`) for running against your environment.

## Troubleshooting
- If Chrome/ChromeDriver version mismatch occurs, install matching versions or use the GitHub Actions setup steps as reference.
- Ensure `chromedriver` is on PATH: `which chromedriver`.
- If elements aren't found, update the locators in `login_page.py`.
- If tests fail due to navigation timing, ensure your app is available and stable; adjust waits if necessary.

## License
MIT
