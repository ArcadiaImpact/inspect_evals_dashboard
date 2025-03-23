import pytest
from pytest import MonkeyPatch
from src.config import EvaluationConfig


def test_substitute_env_vars_replaces_variables():
    with MonkeyPatch.context() as mp:
        # Setup environment variables
        mp.setenv("TEST_BUCKET", "my-test-bucket")
        mp.setenv("ENVIRONMENT", "test")

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
    with MonkeyPatch.context() as mp:
        mp.setenv("VAR1", "first")
        mp.setenv("VAR2", "second")

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
