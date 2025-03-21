# from inspect_evals_scoring.process_log import DashboardLog
from inspect_evals_dashboard_schema import DashboardLog
import numpy as np
import pandas as pd
import streamlit as st


@st.cache_data(hash_funcs={DashboardLog: id})
def create_pairwise_analysis_table(
    eval_logs: list[DashboardLog],
    model_name: str,
    baseline_name: str,
    metric_name: str,
    score_name: str = None,
):
    rows = []

    task_groups = {}
    for log in eval_logs:
        task = log.eval.task
        if task not in task_groups:
            task_groups[task] = []
        task_groups[task].append(log)

    for task, logs in task_groups.items():
        model_log = next((log for log in logs if model_name == log.eval.model), None)
        baseline_log = next((log for log in logs if baseline_name == log.eval.model), None)

        if model_log and baseline_log:
            # Find the correct score objects by name if score name is provided
            if score_name:
                model_score = next((score for score in model_log.results.scores if score.name == score_name), None)
                baseline_score = next((score for score in baseline_log.results.scores if score.name == score_name), None)
            else:
                # Use the first score object if no score name is provided
                model_score = model_log.results.scores[0]
                baseline_score = baseline_log.results.scores[0]

            if not model_score or not baseline_score:
                break

            # Extract values using the specified metric name
            model_acc = model_score.metrics[metric_name].value
            model_se = model_score.metrics["stderr"].value
            baseline_acc = baseline_score.metrics[metric_name].value
            baseline_se = baseline_score.metrics["stderr"].value

            # Calculate difference
            diff = model_acc - baseline_acc

            # Using the formula: SE_unpaired = sqrt(SE_A^2 + SE_B^2)
            combined_se = np.sqrt(model_se**2 + baseline_se**2)

            # Calculate confidence interval and z-score using the appropriate SE
            ci_lower = diff - 1.96 * combined_se
            ci_upper = diff + 1.96 * combined_se
            z_score = diff / combined_se

            rows.append({
                "Task": task.removeprefix("inspect_evals/"),
                "# Questions": model_log.results.completed_samples,
                "Model": model_name,
                "Baseline": baseline_name,
                "Model - Baseline": f"{diff*100:.2f}% ({combined_se*100:.2f}%)",
                "95% Conf. Interval": f"({ci_lower*100:.2f}%, {ci_upper*100:.2f}%)",
                "z-score": f"{z_score:.2f}",
            })

    return pd.DataFrame(rows)
