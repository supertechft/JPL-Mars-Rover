#!/usr/bin/env bash
# Copyright (c) 2024. Jet Propulsion Laboratory. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script launches the ROSA demo in Docker

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker and try again."
    exit 1
fi

# Set default headless mode
HEADLESS=${HEADLESS:-false}
DEVELOPMENT=${DEVELOPMENT:-true}
# true to be able to see changes in the src/rosa folder
# false for regular jpl-rosa package

# Enable X11 forwarding based on OS
case "$(uname)" in
    Linux*|Darwin*)
        echo "Enabling X11 forwarding..."

        # Credits user Giuseppe Coco for this change
        # If running under WSL, use :0 for DISPLAY
        if grep -q "WSL" /proc/version; then
            export DISPLAY=:0
        else
            export DISPLAY=:0
            # try DISPLAY=host.docker.internal:0 if DISPLAY=:0 doesn't work
        fi
        xhost +
        ;;
    MINGW*|CYGWIN*|MSYS*)
        echo "Enabling X11 forwarding for Windows..."
        export DISPLAY=host.docker.internal:0
        ;;
    *)
        echo "Error: Unsupported operating system."
        exit 1
        ;;
esac

# Check if X11 forwarding is working
if ! xset q &>/dev/null; then
    echo "Error: X11 forwarding is not working. Please check your X11 server and try again."
    exit 1
fi

# Build and run the Docker container
CONTAINER_NAME="rosa-turtlesim-demo"

# comment out these two lines below if you just want to run
echo "Building the $CONTAINER_NAME Docker image..."
sudo docker build --build-arg DEVELOPMENT=$DEVELOPMENT -t $CONTAINER_NAME -f Dockerfile . || { echo "Error: Docker build failed"; exit 1; }

echo "Running the Docker container..."
sudo docker run -it --rm --device /dev/snd --name $CONTAINER_NAME \
    -e DISPLAY=$DISPLAY \
    -e HEADLESS=$HEADLESS \
    -e DEVELOPMENT=$DEVELOPMENT \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v "$PWD/src":/app/src \
    -v "$PWD/tests":/app/tests \
    --network host \
    $CONTAINER_NAME

# Disable X11 forwarding
xhost -

exit 0
