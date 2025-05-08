import streamlit as st

st.title("Changelog")

st.markdown("""
            All notable changes to this project will be documented in this file.

            The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
            and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

            ## [0.1.1] - 2025-05-06
            ### Changed
            - [FIX] KeyError 'date' when bar chart value is zero (#48)
            - Update config (#51)
            - Fix double counting models, evals, runs on home page (#54)
            - Update prod config after promoting runs (#53)
            - Set location of dashboard logs from downloaded path (#52)

            ## [0.1.0] - 2025-03-31
            ### Changed
            - Initial release of the Inspect Evals Dashboard.
""")
