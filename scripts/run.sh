#!/bin/bash
python3 -m uvicorn qabot.main:app --host 0.0.0.0 --port 1447
