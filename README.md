# Inspect Evaluations Dashboard

A Streamlit-based web application for visualizing results of AI evaluations based on open source implementations from the [`inspect_evals`](https://github.com/UKGovernmentBEIS/inspect_evals) library.

## Project Structure

```bash
├── app.py
├── config.yml
├── .env
├── requirements.txt
├── pyproject.toml
├── .streamlit
│   └── config.toml
├── src
│   ├── pages
│   │   ├── evaluations
│   │   │   ├── agents.py
│   │   │   ├── assistants.py
│   │   │   ├── coding.py
│   │   │   ├── cybersecurity.py
│   │   │   ├── knowledge.py
│   │   │   ├── mathematics.py
│   │   │   ├── reasoning.py
│   │   │   └── safeguards.py
│   │   ├── page_utils.py
│   │   ├── changelog.py
│   │   └── docs.py
│   └── plots
│       └── bar.py
└── utils
    └── config.py
```

## Setup and Installation

1. Clone this repository:

```bash
git clone https://github.com/ArcadiaImpact/inspect_evals_dashboard.git
cd inspect_evals_dashboard
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

4. Set up environment variables in `.env`:

```env
STREAMLIT_ENV=dev
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=your_region
```

5. Run the application:

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Pages Description

- **Home**: Landing page with project overview and main features
- **Evaluations**: Contains subpages for different evaluation categories
  - Agents: Assessment of AI agentic capabilities
  - Assistants: Evaluation of AI assistant features
  - Coding: Evaluate AI coding capabilities
  - Cybersecurity: Assessment of security understanding
  - Knowledge: General knowledge evaluation
  - Mathematics: Testing mathematical problem-solving abilities
  - Reasoning: Logic and reasoning capabilities assessment
  - Safeguards: Evaluation of AI safety measures
- **Documentation**: Detailed documentation about the evaluation methodologies
- **Changelog**: Version history and updates

## Configuration

The application supports different environments (dev, stage, prod) configured through `config.yml`.
Set the environment using the STREAMLIT_ENV environment variable:

```bash
# For development (default)
streamlit run app.py

# For staging
STREAMLIT_ENV=stage streamlit run app.py

# For production
STREAMLIT_ENV=prod streamlit run app.py
```

### Environment Variables

- `STREAMLIT_ENV`: Environment to use (dev/stage/prod). Defaults to 'dev'
- `AWS_ACCESS_KEY_ID`: AWS access key for S3 access
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for S3 access
- `AWS_DEFAULT_REGION`: AWS region for S3 access

### Configuration Files

- `.streamlit/config.toml`: Streamlit-specific configuration
- `config.yml`: Environment-specific configuration including:
  - Evaluation configurations
  - S3 paths for data storage
  - Default scorers and metrics
