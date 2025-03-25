# Inspect Evaluations Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://inspect-evals-dashboard.streamlit.app/)

A Streamlit-based web application for visualizing results of AI evaluations based on open source implementations from the [`inspect_evals`](https://github.com/UKGovernmentBEIS/inspect_evals) library.

## Project Structure

```bash
├── app.py
├── config.yml
├── requirements.txt
├── pyproject.toml
├── Makefile
├── .streamlit
│   ├── config.toml
│   └── secrets.toml
├── tests
├── src
│   ├── pages
│   │   ├── evaluations
│   │   │   ├── agents.py
│   │   │   ├── assistants.py
│   │   │   ├── coding.py
│   │   │   ├── cybersecurity.py
│   │   │   ├── knowledge.py
│   │   │   ├── mathematics.py
│   │   │   ├── multimodal.py
│   │   │   ├── reasoning.py
│   │   │   ├── safeguards.py
│   │   │   └── template.py
│   │   ├── changelog.py
│   │   └── docs.py
│   ├── plots
│   │   ├── bar.py
│   │   ├── cutoff_scatter.py
│   │   ├── pairwise.py
│   │   ├── radar.py
│   │   └── plot_utils.py
│   ├── log_utils
│   │   ├── dashboard_log_utils.py
│   │   └── load_eval_logs.py
│   └── config.py
```

## Setup and Installation

- Recommended Python version: Python 3.12+

1. Clone this repository:

```bash
git clone https://github.com/ArcadiaImpact/inspect_evals_dashboard.git
cd inspect_evals_dashboard
```

1. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

1. Install required packages:

```bash
# For running the app
pip install .

# For development
pip install .[dev]
```

1. Set up environment variables in `.streamlit/secrets.toml`:

```toml
STREAMLIT_ENV = "dev"
AWS_ACCESS_KEY_ID = "your_access_key"
AWS_SECRET_ACCESS_KEY = "your_secret_key"
AWS_DEFAULT_REGION = "eu-west-2"
AWS_S3_BUCKET = "you_bucket"
```

1. Run the application:

```bash
streamlit run app.py
```

### Development Tools

The project includes several development tools and configurations:

- **Pre-commit Hooks**: Configured in `.pre-commit-config.yaml` for code quality checks
- **Type Checking**: Using `mypy` for static type checking
- **Linting**: Using `ruff` for Python linting
- **Testing**: Using `pytest` for unit tests
- **Make Commands**: Common development tasks are available via `make` commands

### Run Tests

```bash
make test
```

### Install pre-commit hooks

```bash
make hooks-install
```

### Update pre-commit hooks

```bash
make hooks-update
```

### Run code quality checks

```bash
make check
```

The application will be available at `http://localhost:8501`

## Pages Description

- **Home**: Landing page with project overview and main features
- **Evaluations**: Contains subpages for different evaluation categories:
  - Agents
  - Assistants
  - Coding
  - Cybersecurity
  - Knowledge
  - Mathematics
  - Reasoning
  - Safeguards
- **Documentation**: Detailed documentation about the evaluation methodologies
- **Changelog**: Version history and updates

## Configuration

The application supports different environments (test, dev, stage, prod) configured through `config.yml`.
Set the environment using the `STREAMLIT_ENV` environment variable:

```bash
# For development (default)
streamlit run app.py

# For staging
STREAMLIT_ENV=stage streamlit run app.py

# For production
STREAMLIT_ENV=prod streamlit run app.py

# For development
STREAMLIT_ENV=dev streamlit run app.py
```

### Environment Variables

- `STREAMLIT_ENV`: Environment to use (test/dev/stage/prod). Defaults to 'dev'
- `AWS_ACCESS_KEY_ID`: AWS access key for S3 access
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for S3 access
- `AWS_DEFAULT_REGION`: AWS region for S3 access
- `AWS_S3_BUCKET`: AWS S3 bucket name to read logs from

### Configuration Files

- `.streamlit/config.toml`: Streamlit-specific configuration
- `config.yml`: Environment-specific configuration including:
  - Evaluation configurations
  - S3 paths for data storage
  - Default scorers and metrics
- `.pre-commit-config.yaml`: Pre-commit hooks configuration
- `.markdownlint.yml`: Markdown linting rules
- `pyproject.toml`: Project metadata and tool configurations
