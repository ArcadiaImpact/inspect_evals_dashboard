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


def parse_paths(paths_file=None):
    if paths_file:
        with open(paths_file, "r") as f:
            paths = f.readlines()
        paths = [path.strip() for path in paths if path.strip()]
    else:
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
    # First try to match the ISO timestamp format in the filename
    match = re.search(r"(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2})", path)
    if match:
        return match.group(1)

    # Default to empty string if no timestamp found
    return ""


def extract_environment(path):
    if "logs/stage/" in path:
        return "stage"
    elif "logs/prod/" in path:
        return "prod"
    elif "logs/dev/" in path:
        return "dev"
    return "dev"  # Default to dev if not found


def extract_default_metrics(path):
    # This is a stub - in reality, you would download and parse the JSON file
    # For GSM8K, typically use "match" scorer
    if "gsm8k" in path.lower():
        return "match", "accuracy"
    # For most other evaluations, use "choice" scorer
    return "choice", "accuracy"


def create_config(paths_list):
    # Group paths by environment and evaluation name
    env_eval_paths = defaultdict(lambda: defaultdict(list))
    for path in paths_list:
        env = extract_environment(path)
        eval_name = extract_eval_name(path)
        if eval_name:
            env_eval_paths[env][eval_name].append(path)

    # Create YAML config maintaining order
    config = {}

    # Create sections for each environment
    for env in sorted(env_eval_paths.keys()):
        config[env] = {"evaluations": {}}

        # Create sections for each category in the mapping
        for category, evals in MAPPING.items():
            config[env]["evaluations"][category] = []

            # Track if we've added any evaluations for this category
            category_has_evals = False

            # Add each evaluation in this category
            for eval_name in evals:
                eval_name_normalized = eval_name.lower().replace("-", "_")

                if eval_name_normalized in env_eval_paths[env]:
                    category_has_evals = True

                    # Get default scorer and metric from the file
                    default_scorer, default_metric = extract_default_metrics(
                        env_eval_paths[env][eval_name_normalized][0]
                    )

                    eval_config = {
                        "name": eval_name_normalized,
                        "default_scorer": default_scorer,
                        "default_metric": default_metric,
                        "paths": [
                            f"s3://$AWS_S3_BUCKET/{path}"
                            for path in env_eval_paths[env][eval_name_normalized]
                        ],
                    }

                    config[env]["evaluations"][category].append(eval_config)

            # If no evaluations were added for this category, add placeholder
            if not category_has_evals:
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


# Check for inconsistencies in the config:
# Same logs in different parts of the config having different settings
# Inconsistencies with MAPPING
# Missing default_choice, default_metric
def check_inconsistencies(config):
    # Create a dictionary to track all paths and their settings
    path_settings = {}
    inconsistencies = []

    # Check for duplicate paths with different settings
    for env, env_config in config.items():
        for category, evals in env_config["evaluations"].items():
            for eval_config in evals:
                for path in eval_config["paths"]:
                    path_key = (
                        path.split("s3://$AWS_S3_BUCKET/")[1]
                        if "s3://$AWS_S3_BUCKET/" in path
                        else path
                    )

                    settings = {
                        "default_scorer": eval_config["default_scorer"],
                        "default_metric": eval_config["default_metric"],
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


def main():
    parser = argparse.ArgumentParser(description="Generate YAML config for dashboard.")
    parser.add_argument("--output", help="Output file for YAML config (optional)")
    args = parser.parse_args()

    # Parse paths  from S3
    paths_list = parse_paths()

    # Generate config
    config = create_config(paths_list)

    # Convert to YAML
    yaml_config = yaml.dump(config, sort_keys=False, default_flow_style=False)

    # Output
    if args.output:
        with open(args.output, "w") as f:
            f.write(yaml_config)
    else:
        print(yaml_config)


if __name__ == "__main__":
    main()
