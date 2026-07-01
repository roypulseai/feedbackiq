#!/bin/bash
IMAGE_NAME="feedbackiq"
TAR_FILE="${IMAGE_NAME}.tar"

echo "==================================================="
echo "Building FeedbackIQ..."
echo "==================================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed or not in PATH."
    echo "Please install Docker Desktop from https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "ERROR: Docker is not running."
    echo "Please start Docker Desktop and wait for it to be ready."
    exit 1
fi

echo "[1/2] Building Docker image..."
echo "This will download ML models (~4-6 GB) on first run."
echo ""
docker build -t "$IMAGE_NAME" .
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Docker build failed. Check the output above."
    exit 1
fi

echo ""
echo "[2/2] Exporting image to $TAR_FILE ..."
docker save -o "$TAR_FILE" "$IMAGE_NAME"
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to export image. Check disk space."
    exit 1
fi

echo ""
echo "==================================================="
echo "Build complete!"
echo "==================================================="
echo ""
echo "You can now run FeedbackIQ by double-clicking Start_App.bat (Windows)"
echo "or running Start_App.command (macOS)."
echo ""
echo "  Image:  $IMAGE_NAME"
echo "  Export: $TAR_FILE"
echo ""
