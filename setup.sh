#!/bin/bash

mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = ${PORT:-8501}\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
