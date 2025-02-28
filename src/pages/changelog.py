import streamlit as st

# TODO:
# * Replace this example with an actual first entry to the changelog

st.title("Changelog")

st.markdown("""
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [14.1.0] - 2024-03-19
### Changed
- Updated CM spec compatibility to 0.31.2, #1009.

### Fixed
- Fixed quadratic complexity when parsing references, #996.
- Fixed quadratic output size with pathological user input in tables, #1000.


## [14.0.0] - 2023-12-08
### Changed
- Drop ancient browsers support (use `.fromCodePoint` and other features).
- Rewrite to ESM (including all plugins/deps). CJS fallback still available.
  No signatures changed, except `markdown-it-emoji` plugin.
- Dropped `dist/` folder from repo, build on package publish.
- Set `punicode.js` as external dependency.
""")
