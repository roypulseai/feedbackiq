@echo off
set IMAGE_NAME=feedbackiq

echo ===================================================
echo Starting FeedbackIQ...
echo ===================================================

if exist feedbackiq.tar (
    echo [1/2] Loading Docker image from feedbackiq.tar...
    docker load -i feedbackiq.tar
) else (
    echo [1/2] feedbackiq.tar not found - checking for locally built image...
    docker image inspect %IMAGE_NAME% >nul 2>&1
    if errorlevel 1 (
        echo.
        echo ERROR: Docker image '%IMAGE_NAME%' not found.
        echo.
        echo To build the image from source, run:
        echo   docker build -t %IMAGE_NAME% .
        echo.
        echo Or obtain feedbackiq.tar from your developer and place it
        echo in the same folder as this script.
        echo.
        pause
        exit /b 1
    ) else (
        echo Found locally built image.
    )
)

echo [2/2] Starting FeedbackIQ at http://localhost:8501 ...
echo.
echo Press Ctrl+C in this window to stop the app.
echo.
start http://localhost:8501
docker run -p 8501:8501 %IMAGE_NAME%

echo.
echo ===================================================
echo FeedbackIQ has stopped.
echo ===================================================
echo.
echo To restart, run this script again.
echo To stop Docker Desktop, right-click the Docker whale icon
echo in the system tray and select Quit.
echo.
pause
