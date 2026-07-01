#!/bin/bash
echo "==================================================="
echo "Starting FeedbackIQ..."
echo "==================================================="
cd "$(dirname "$0")"
docker load -i feedbackiq.tar
open http://localhost:8501
docker run -p 8501:8501 feedbackiq
