@echo off
echo ===================================================
echo Starting FeedbackIQ...
echo ===================================================
docker load -i feedbackiq.tar
start http://localhost:8501
docker run -p 8501:8501 feedbackiq
pause
