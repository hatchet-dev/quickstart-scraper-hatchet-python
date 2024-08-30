#!/bin/bash

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install Python3 and try again."
    exit 1
fi

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry is not installed. Please install Poetry using the following command:"
    echo "curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Check if .env file exists and contains HATCHET_CLIENT_TOKEN
if [ ! -f backend/.env ] || ! grep -q "HATCHET_CLIENT_TOKEN" backend/.env; then
    echo "Error: HATCHET_CLIENT_TOKEN not found in backend/.env file."
    echo "Please set up your Hatchet API Key in the backend/.env file."
    echo "You can get your API key from the Hatchet dashboard."
    exit 1
fi

# Function to open a new terminal window and run a command
open_terminal_and_run() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        osascript -e "tell app \"Terminal\" to do script \"cd $(pwd) && $1\""
    else
        # Linux (assuming X11)
        if command -v xterm &> /dev/null; then
            xterm -e "cd $(pwd) && $1" &
        else
            echo "xterm is not installed. Please install xterm or modify the script to use your preferred terminal emulator."
            exit 1
        fi
    fi
}

# Install backend dependencies
cd backend
poetry install
cd ..

# Start the backend API
open_terminal_and_run "cd backend && poetry run start-api"

# Start the Hatchet worker
open_terminal_and_run "cd backend && poetry run start-worker"

# Start the frontend
open_terminal_and_run "cd frontend && npm install && npm run dev"

echo "All services have been started in separate terminal windows."

# Wait for a few seconds to allow services to start
sleep 5

# Open the default browser with the webpage
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "http://localhost:3000"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "http://localhost:3000"
else
    echo "Unsupported operating system. Please open http://localhost:3000 in your browser manually."
fi