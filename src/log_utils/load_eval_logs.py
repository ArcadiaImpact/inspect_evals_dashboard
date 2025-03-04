import json
import os
from itertools import chain
from pathlib import Path

import streamlit as st
# from inspect_evals_scoring.process_log import DashboardLog
from src.log_utils.dashboard_log import DashboardLog
from st_files_connection import FilesConnection


@st.cache_data
def load_evaluation_logs(evaluation_paths: list[str]) -> list[DashboardLog]:
    """
    Load evaluation logs from S3 or local path based on config.

    Args:
        evaluation_paths: List of paths (S3 or local) to evaluation log files

    Returns:
        List of DashboardLog objects
    """

    def load_json_from_s3(path: str, conn: FilesConnection) -> dict:
        return conn.read(path, input_format="json", ttl=600)

    def load_json_from_local(path: str) -> dict:
        with open(Path(path), "r") as f:
            return json.load(f)

    env = os.getenv("STREAMLIT_ENV", "dev")
    conn = None
    if env != "test":
        conn = st.connection("s3", type=FilesConnection)

    dashboard_logs = []
    for path in evaluation_paths:
        if path.startswith("s3://"):
            if conn is None:
                raise ValueError("S3 connection not initialized but S3 path provided")
            data = load_json_from_s3(path, conn)
        else:
            data = load_json_from_local(path)
        dashboard_logs.append(DashboardLog(**data))

    return dashboard_logs


def get_log_paths(config: list[dict]) -> list[str]:
    return list(chain.from_iterable([t["paths"] for t in config]))
