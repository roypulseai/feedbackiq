#!/bin/bash
IMAGE_NAME="feedbackiq"

echo "==================================================="
echo "Starting FeedbackIQ..."
echo "==================================================="
cd "$(dirname "$0")" || exit

if [ -f "feedbackiq.tar" ]; then
    echo "[1/2] Loading Docker image from feedbackiq.tar..."
    docker load -i feedbackiq.tar
else
    echo "[1/2] feedbackiq.tar not found - checking for locally built image..."
    if docker image inspect "$IMAGE_NAME" > /dev/null 2>&1; then
        echo "Found locally built image."
    else
        echo ""
        echo "ERROR: Docker image '$IMAGE_NAME' not found."
        echo ""
        echo "To build the image from source, run:"
        echo "  docker build -t $IMAGE_NAME ."
        echo ""
        echo "Or obtain feedbackiq.tar from your developer and place it"
        echo "in the same folder as this script."
        echo ""
        exit 1
    fi
fi

echo "[2/2] Starting FeedbackIQ at http://localhost:8501 ..."
echo ""
echo "Press Ctrl+C in this terminal to stop the app."
echo ""
open http://localhost:8501
docker run -p 8501:8501 "$IMAGE_NAME"

echo ""
echo "==================================================="
echo "FeedbackIQ has stopped."
echo "==================================================="
echo ""
echo "To restart, run this script again."
echo "To stop Docker Desktop, click the Docker whale icon in"
echo "the menu bar and select Quit."
echo ""
