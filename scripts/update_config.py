import argparse
import json
import os
import re
import sys
from collections import defaultdict

import boto3
import yaml

MAPPING = {
    "agents": [
        "cybench",
        "gaia_level3",
        "gdm_intercode_ctf",
        "osworld",
        "swe_bench_verified_mini",
        "agentharm",
    ],
    "assistants": ["gaia_level3", "agentharm"],
    "coding": ["cybench", "humaneval", "mbpp", "osworld", "swe_bench_verified_mini"],
    "cybersecurity": [
        "cybench",
        "cyse2_vulnerability_exploit",
        "cyse2_interpreter_abuse",
        "cyse2_prompt_injection",
        "gdm_intercode_ctf",
    ],
    "knowledge": ["bbh", "commonsense_qa", "gpqa_diamond", "mmlu_pro"],
    "mathematics": ["bbh", "gsm8k", "mathvista"],
    "multimodal": ["mathvista", "mmmu_open", "mmmu_multiple_choice"],
    "reasoning": [
        "bbh",
        "hellaswag",
        "ifeval",
        "mmmu_open",
        "mmmu_multiple_choice",
        "mmlu_pro",
        "piqa",
    ],
    "safeguards": [
        "agentharm",
        "cyse2_vulnerability_exploit",
        "cyse2_interpreter_abuse",
        "cyse2_prompt_injection",
    ],
}

DASHBOARD_LOG_FILE_SUFFIX = ".dashboard.json"

ENV_ORDER = ["prod", "stage", "dev", "test"]

BUCKET_NAME = os.environ.get("AWS_S3_BUCKET", "inspect-evals-dashboard")


def parse_paths():
    # Get paths directly from S3
    s3 = boto3.client("s3")
    paginator = s3.get_paginator("list_objects_v2")
    result = []

    for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix="logs/"):
        if "Contents" in page:
            for obj in page["Contents"]:
                if obj["Key"].endswith(DASHBOARD_LOG_FILE_SUFFIX):
                    result.append(obj["Key"])

    paths = result

    # Group paths by evaluation-model combination and get the most recent ones
    eval_model_paths = defaultdict(list)
    for path in paths:
        eval_name = extract_eval_name(path)
        model_name = extract_model(path)
        env = extract_environment(path)

        if eval_name and model_name:
            key = f"{env}:{eval_name}:{model_name}"
            eval_model_paths[key].append(path)

    # Sort by date and get the most recent path for each eval-model combination
    result = []
    for _, paths_list in eval_model_paths.items():
        # Sort by timestamp in the path
        sorted_paths = sorted(
            paths_list,
            key=lambda x: extract_timestamp(x),
            reverse=True,  # Most recent first
        )
        # Take the most recent path
        if sorted_paths:
            result.append(sorted_paths[0])

    return result


def extract_eval_name(path):
    """Extract evaluation name from an S3 path."""
    match = re.search(r"logs/[^/]+/([^/]+)/", path)
    if match:
        return match.group(1).lower().replace("-", "_")
    return None


def extract_model(path):
    """Extract model name from an S3 path."""
    match = re.search(r"/([^/]+\+[^/]+)/", path)
    if match:
        return match.group(1)
    return None


def extract_timestamp(path):
    """Extract timestamp from path for sorting by recency."""
    # We support both T and - as a separator
    match = re.search(r"(\d{4}-\d{2}-\d{2}[T-]\d{2}-\d{2}-\d{2})", path)
    if match:
        return match.group(1)

    # Default to empty string if no timestamp found
    return ""


def extract_environment(path):
    if "logs/stage/" in path:
        # For now stage logs count as both stage and dev
        # We don't have a separate dev generation currently, though this might change in the future
        return ["stage", "dev"]
    elif "logs/prod/" in path:
        return ["prod"]
    elif "logs/dev/" in path:
        return ["dev"]
    return ["dev"]  # Default to dev if not found


def get_default_metrics_from_config(original_config, eval_name, env):
    """Search through original config to find default metrics for a given evaluation."""
    if not original_config or not env or env not in original_config:
        return None, None

    # Look through all categories in the config
    if "evaluations" in original_config[env]:
        for category, evals_list in original_config[env]["evaluations"].items():
            for eval_config in evals_list:
                if eval_config.get("name") == eval_name:
                    return (
                        eval_config.get("default_scorer", "choice"),
                        eval_config.get("default_metric", "accuracy"),
                    )
    return None, None


def get_scores_from_file(path):
    """Download and extract scores from the dashboard file."""
    try:
        s3 = boto3.client("s3")
        response = s3.get_object(Bucket=BUCKET_NAME, Key=path)
        data = json.loads(response["Body"].read().decode("utf-8"))

        if "results" in data and "scores" in data["results"]:
            return data["results"]["scores"]
    except Exception:
        print("ERROR: failed to get scores from the file")
        raise

    return []


def extract_default_metrics(path, env_name, original_config=None, eval_name=None):
    """Extract default metrics from dashboard file and validate against original config."""
    # Get values from the original config for the specific environment
    config_scorer = None
    config_metric = None
    if original_config and eval_name and env_name:
        config_scorer, config_metric = get_default_metrics_from_config(
            original_config, eval_name, env_name
        )

    # Get scores from the dashboard file
    scores = get_scores_from_file(path)

    # If we have config values, check if they exist in the file
    if config_scorer and config_metric:
        # Find the scorer in the file
        scorer_matches = [s for s in scores if s["name"] == config_scorer]
        if scorer_matches:
            # Check if the metric exists for this scorer
            metrics = scorer_matches[0].get("metrics", {})
            if config_metric in metrics:
                # Both scorer and metric found in file - use them
                return config_scorer, config_metric
            else:
                raise Exception(
                    f"Metric '{config_metric}' from config not found in file for scorer '{config_scorer}'"
                )

        else:
            raise Exception(
                f"Scorer '{config_scorer}' from config not found in file {path}"
            )

    # If config values don't exist or weren't found in the file, use the first ones from the file
    if scores:
        if len(scores) > 1:
            scorer_names = [score["name"] for score in scores]
            print(
                f"WARNING: Multiple scorers found in {path}: {', '.join(scorer_names)}. Using the first one."
            )

        first_scorer = scores[0]["name"]
        metrics = scores[0].get("metrics", {})

        # Filter out stderr metrics
        non_stderr_metrics = {k: v for k, v in metrics.items() if k != "stderr"}
        if non_stderr_metrics:
            if len(non_stderr_metrics) > 1:
                print(
                    f"WARNING: Multiple metrics found in {path} for the scorer {first_scorer}, using the first one. Metrics: {', '.join(non_stderr_metrics)}"
                )
            first_metric = next(iter(non_stderr_metrics))
            return first_scorer, first_metric
        else:
            raise Exception(
                f"Scorer '{config_scorer}' does not have any metrics in file {path}"
            )

    return "choice", "accuracy"


def create_config(paths_list, original_config=None):
    # Group paths by environment and evaluation name
    env_eval_paths = defaultdict(lambda: defaultdict(list))
    for path in paths_list:
        envs = extract_environment(path)
        eval_name = extract_eval_name(path)
        if eval_name:
            for env in envs:
                env_eval_paths[env][eval_name].append(path)

    # Create YAML config
    config = {}

    # Process environments in the specified order
    for env in ENV_ORDER:
        # For 'test' environment, take directly from original config if available
        if env == "test" and original_config and "test" in original_config:
            config["test"] = original_config["test"]
            continue

        # Skip environments that don't have any paths and aren't in original config
        if env not in env_eval_paths and (
            not original_config or env not in original_config
        ):
            continue

        config[env] = {"evaluations": {}}

        for category in sorted(MAPPING.keys()):
            config[env]["evaluations"][category] = []

            # Track if we've added any evaluations for this category
            category_has_evals = False

            # Sort evaluations lexicographically within each category
            evals_in_category = sorted(
                [e for e in MAPPING[category] if e in env_eval_paths[env]]
            )

            # Add each evaluation in this category
            for eval_name in evals_in_category:
                category_has_evals = True

                # Get default scorer and metric from original config or fallback
                default_scorer, default_metric = extract_default_metrics(
                    env_eval_paths[env][eval_name][0], env, original_config, eval_name
                )

                eval_config = {
                    "name": eval_name,
                    "default_scorer": default_scorer,
                    "default_metric": default_metric,
                    "paths": [
                        f"s3://$AWS_S3_BUCKET/{path}"
                        for path in sorted(env_eval_paths[env][eval_name])
                    ],
                }

                config[env]["evaluations"][category].append(eval_config)

            # If no evaluations were added for this category but it exists in original config, take the whole section
            if not category_has_evals:
                if (
                    original_config
                    and env in original_config
                    and "evaluations" in original_config[env]
                    and category in original_config[env]["evaluations"]
                ):
                    # Use all evaluations from original config for this category
                    config[env]["evaluations"][category] = original_config[env][
                        "evaluations"
                    ][category]
                else:
                    raise Exception(f'No evaluations for category "{category}"')

    # Check for inconsistencies
    check_inconsistencies(config, env_eval_paths)

    return config


def check_inconsistencies(config, env_eval_paths):
    # Create a dictionary to track all paths and their settings
    path_settings = {}
    inconsistencies = []

    # Check for evals not in any category in MAPPING
    all_mapped_evals = set()
    for category, evals in MAPPING.items():
        all_mapped_evals.update(evals)

    # Check each environment for evals that aren't in MAPPING
    for env, eval_to_paths in env_eval_paths.items():
        for eval_name in eval_to_paths.keys():
            if eval_name not in all_mapped_evals:
                inconsistencies.append(
                    f"Eval '{eval_name}' in environment '{env}' is not in any category in MAPPING"
                )

    # Check for duplicate paths with different settings
    for env, env_config in config.items():
        for category, evals in env_config["evaluations"].items():
            for eval_config in evals:
                for path in eval_config.get("paths", []):
                    path_key = (
                        path.split("s3://$AWS_S3_BUCKET/")[1]
                        if "s3://$AWS_S3_BUCKET/" in path
                        else path
                    )

                    settings = {
                        "default_scorer": eval_config.get("default_scorer", "choice"),
                        "default_metric": eval_config.get("default_metric", "accuracy"),
                    }

                    if path_key in path_settings:
                        # Check if settings are different
                        if path_settings[path_key] != settings:
                            inconsistencies.append(
                                f"Inconsistency found for path {path_key}: {path_settings[path_key]} vs {settings}"
                            )
                    else:
                        path_settings[path_key] = settings

    # Check for inconsistencies with MAPPING
    for env, env_config in config.items():
        # Skip test environment and non-dictionary configs
        if env == "test":
            continue

        for category, evals in env_config["evaluations"].items():
            if category in MAPPING:
                for eval_config in evals:
                    eval_name = eval_config["name"]

                    if eval_name not in MAPPING[category]:
                        inconsistencies.append(
                            f"Inconsistency with MAPPING: {eval_name} in category {category} not in MAPPING"
                        )

    # Check for missing default_choice, default_metric
    for env, env_config in config.items():
        for category, evals in env_config["evaluations"].items():
            for eval_config in evals:
                if "default_scorer" not in eval_config:
                    inconsistencies.append(
                        f"Missing default_scorer in {env}/{category}/{eval_config['name']}"
                    )
                if "default_metric" not in eval_config:
                    inconsistencies.append(
                        f"Missing default_metric in {env}/{category}/{eval_config['name']}"
                    )

    # Print inconsistencies
    if inconsistencies:
        print("WARNING: The following inconsistencies were found:")
        for inconsistency in inconsistencies:
            print(f"  - {inconsistency}")

        raise Exception("Inconsistencies found, not writing the config")


def extract_comments(file_path):
    """Extract comments from the top of the original file."""
    comments = []
    if not os.path.exists(file_path):
        return comments

    with open(file_path, "r") as f:
        for line in f:
            if line.strip().startswith("#"):
                comments.append(line.rstrip())
            elif not line.strip():
                # Keep empty lines between comments
                if comments and comments[-1]:
                    comments.append("")
            else:
                # Stop once we hit non-comment, non-empty line
                break

    return comments


def main():
    parser = argparse.ArgumentParser(
        description="Automatically generate and validate a YAML config from S3",
        epilog="Example: python3 scripts/update_config.py --input config.yml --output config.yml",
    )

    parser.add_argument(
        "--input",
        help="Original YAML config file to get default metrics from",
        required=True,
    )
    parser.add_argument("--output", help="Output file for YAML config", required=True)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    # Load original config if provided
    original_config = None
    comments = []
    if args.input:
        # Extract comments from the top of the file
        comments = extract_comments(args.input)

        # Load the YAML content
        with open(args.input, "r") as f:
            original_config = yaml.safe_load(f)

    # Parse paths from file or S3
    paths_list = parse_paths()

    # Generate config
    config = create_config(paths_list, original_config)

    # Convert to YAML
    yaml_config = yaml.dump(config, sort_keys=False, default_flow_style=False)

    # Prepend comments
    if comments:
        yaml_config = "\n".join(comments) + "\n" + yaml_config

    with open(args.output, "w") as f:
        f.write(yaml_config)


if __name__ == "__main__":
    main()
