#!/bin/bash
cd /Users/muthuvelp/work/local-rag-ollama/backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
