#!/bin/bash
echo "Starting Agentic AI Caller Lead Generation & Outreach Engine..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
