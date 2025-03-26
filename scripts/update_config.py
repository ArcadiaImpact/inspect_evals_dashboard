import argparse
import os
import re
from collections import defaultdict

import boto3
import yaml

MAPPING = {
    "agents": ["cybench", "gaia", "gdm", "piqa", "swe_bench"],
    "assistants": ["gaia", "piqa"],
    "coding": ["cybench", "humaneval", "mbpp", "osworld", "swe_bench"],
    "cybersecurity": [
        "cybench",
        "cyse2_vulnerability_exploit",
        "cyse2_interpreter_abuse",
        "cyse2_prompt_injection",
        "gdm",
    ],
    "knowledge": ["commonsense_qa", "gpqa_diamond", "mmlu_pro"],
    "mathematics": ["gsm8k", "mathvista"],
    "multimodal": ["mathvista", "mmmu_open", "mmmu_multiple_choice"],
    "reasoning": [
        "bbh",
        "hellaswag",
        "ifeval",
        "mmmu_open",
        "mmmu_multiple_choice",
        "mmlu_pro",
    ],
    "safeguards": ["agentharm"],
}

ENV_ORDER = ["prod", "stage", "dev", "test"]


def parse_paths():
    # Get paths directly from S3
    s3 = boto3.client("s3")
    paginator = s3.get_paginator("list_objects_v2")
    bucket = os.environ.get("AWS_S3_BUCKET", "inspect-evals-dashboard")
    result = []

    for page in paginator.paginate(Bucket=bucket, Prefix="logs/stage/"):
        if "Contents" in page:
            for obj in page["Contents"]:
                if obj["Key"].endswith("dashboard.json"):
                    result.append(obj["Key"])

    paths = result

    # Group paths by evaluation-model combination and get the most recent ones
    eval_model_paths = defaultdict(list)
    for path in paths:
        eval_name = extract_eval_name(path)
        model_name = extract_model(path)

        if eval_name and model_name:
            key = f"{eval_name}:{model_name}"
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
    match = re.search(r"logs/stage/([^/]+)/", path)
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
        # Stage logs count as both stage and dev
        return ["stage", "dev"]
    elif "logs/prod/" in path:
        return ["prod"]
    elif "logs/dev/" in path:
        return ["dev"]
    return ["dev"]  # Default to dev if not found


def get_default_metrics_from_config(original_config, eval_name, env="staging"):
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


def extract_default_metrics(path, original_config=None, eval_name=None):
    """Extract default metrics from original config if available, or use fallback values."""
    # First try to get values from original config
    if original_config and eval_name:
        # Try all environments in order
        for env in ENV_ORDER:
            default_scorer, default_metric = get_default_metrics_from_config(
                original_config, eval_name, env
            )
            if default_scorer and default_metric:
                return default_scorer, default_metric

    # Fallback to static logic
    if "gsm8k" in path.lower():
        return "match", "accuracy"
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
                    env_eval_paths[env][eval_name][0], original_config, eval_name
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
                    # If not in original config, add placeholder
                    placeholder = {
                        "name": "pubmedqa",
                        "default_scorer": "choice",
                        "default_metric": "accuracy",
                        "paths": [
                            f"s3://$AWS_S3_BUCKET/{env}/pubmedqa/{i}.json"
                            for i in range(1, 6)
                        ],
                    }
                    config[env]["evaluations"][category].append(placeholder)

    # Check for inconsistencies
    check_inconsistencies(config)

    return config


def check_inconsistencies(config):
    # Create a dictionary to track all paths and their settings
    path_settings = {}
    inconsistencies = []

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
                    if eval_config["name"] != "pubmedqa":  # Skip placeholders
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
    parser = argparse.ArgumentParser(description="Generate YAML config for dashboard.")
    parser.add_argument(
        "--input", help="Original YAML config file to get default metrics from"
    )
    parser.add_argument("--output", help="Output file for YAML config (optional)")
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

    # Output
    if args.output:
        with open(args.output, "w") as f:
            f.write(yaml_config)
    else:
        print(yaml_config)


if __name__ == "__main__":
    main()
