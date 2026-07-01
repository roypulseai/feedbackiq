@echo off
set IMAGE_NAME=feedbackiq
set TAR_FILE=%IMAGE_NAME%.tar

echo ===================================================
echo Building FeedbackIQ...
echo ===================================================
echo.

REM Check if Docker is installed
where docker >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not in PATH.
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop/
    echo Then run this script again.
    echo.
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running.
    echo Please start Docker Desktop and wait for it to be ready.
    echo.
    pause
    exit /b 1
)

echo [1/2] Building Docker image...
echo This will download ML models (~4-6 GB) on first run.
echo.
docker build -t %IMAGE_NAME% .
if errorlevel 1 (
    echo.
    echo ERROR: Docker build failed. Check the output above for details.
    echo.
    pause
    exit /b 1
)

echo.
echo [2/2] Exporting image to %TAR_FILE% ...
docker save -o %TAR_FILE% %IMAGE_NAME%
if errorlevel 1 (
    echo.
    echo ERROR: Failed to export image. Check disk space.
    echo.
    pause
    exit /b 1
)

echo.
echo ===================================================
echo Build complete!
echo ===================================================
echo.
echo You can now run FeedbackIQ by double-clicking Start_App.bat
echo.
echo   Image:  %IMAGE_NAME%
echo   Export: %TAR_FILE% (%IMAGE_NAME%.tar)
echo.
pause
