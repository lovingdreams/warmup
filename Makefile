SHELL := /bin/bash

env-setup:
        rm -rf venv
        python3 -m venv venv; \
        source venv/bin/activate; \
        pip install -r requirements.txt

pre-commit-mac:
        brew install pre-commit
        pre-commit install
        pre-commit run --all-files

run-local:
        source venv/bin/activate; \
        python gmail_chrome_bot.py

run-dev:
        source venv/bin/activate; \
        python gmail_chrome_bot.py

run-stage:
        source venv/bin/activate; \
        python gmail_chrome_bot.py

run-demo:
        source venv/bin/activate; \
        python gmail_chrome_bot.py

run-app: server-env-setup
        source venv/bin/activate; \
        python gmail_chrome_bot.py
