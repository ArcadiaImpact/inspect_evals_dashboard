import re

import pytest
from src.config import EvaluationConfig, load_config


def test_substitute_env_vars_replaces_variables(monkeypatch):
    # Setup environment variables
    monkeypatch.setenv("TEST_BUCKET", "my-test-bucket")
    monkeypatch.setenv("ENVIRONMENT", "test")

    # Test data
    config = EvaluationConfig(
        name="test_eval",
        default_scorer="choice",
        default_metric="accuracy",
        paths=[
            "s3://$TEST_BUCKET/$ENVIRONMENT/data.json",
            "s3://$TEST_BUCKET/fixed/path.json",
            "local/path/no/variables.json",
        ],
    )

    # Assert within the patched context
    assert config.paths == [
        "s3://my-test-bucket/test/data.json",
        "s3://my-test-bucket/fixed/path.json",
        "local/path/no/variables.json",
    ]


def test_substitute_env_vars_multiple_variables(monkeypatch):
    monkeypatch.setenv("VAR1", "first")
    monkeypatch.setenv("VAR2", "second")

    # Test data with multiple variables
    config = EvaluationConfig(
        name="test_eval",
        default_scorer="choice",
        default_metric="accuracy",
        paths=["$VAR1/$VAR2/$VAR1-$VAR2.json"],
    )

    # Assert
    assert config.paths == ["first/second/first-second.json"]


def test_substitute_env_vars_missing_variable(monkeypatch):
    # Ensure the variable doesn't exist
    monkeypatch.delenv("MISSING_VAR", raising=False)

    # Test data with missing variable
    with pytest.raises(Exception) as excinfo:
        EvaluationConfig(
            name="test_eval",
            default_scorer="choice",
            default_metric="accuracy",
            paths=["s3://$MISSING_VAR/test.json"],
        )

    # Assert
    assert "Unable to substitute an environment variable" in str(excinfo.value)
    assert "$MISSING_VAR" in str(excinfo.value)


def test_duplicate_entries(monkeypatch):
    def guess_model_name_from_path(path):
        pattern = r"/([^/]+?\+[^/]+?)/"
        match = re.search(pattern, path)

        if match:
            model_name = match.group(1)
            return model_name.replace("+", "/")
        return None

    # get the function without @st.cache_data decorator
    noncached_load_config = load_config.__wrapped__
    monkeypatch.setenv("AWS_S3_BUCKET", "__test-bucket")

    for env in ["prod", "stage", "dev"]:
        monkeypatch.setenv("STREAMLIT_ENV", env)

        config = noncached_load_config()
        for field in config.model_fields.keys():
            group_config = getattr(config, field)
            for eval_config in group_config:
                # We are currently using paths like /dev/pubmedqa/1.json as placeholders
                # TODO: remove the `if '/dev/pubmedqa/' not in path` part once we have a proper config
                print("eval_config", eval_config)
                print("group_config", group_config)
                print("paths", eval_config.paths)
                model_names = [
                    guess_model_name_from_path(path)
                    for path in eval_config.paths
                    if "/dev/pubmedqa/" not in path
                ]
                assert len(model_names) == len(set(model_names)), (
                    f"Duplicate models in {env}→{field}→{eval_config.name} paths"
                )
