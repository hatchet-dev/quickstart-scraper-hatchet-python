# Hatchet Scraper Example Backend

This is the backend component of the Hatchet Scraper Example project, demonstrating how to use Hatchet with FastAPI for web scraping tasks.

## Prerequisites

Before running this project, make sure you have the following:

1. Python 3.12 or higher installed on your machine.
2. Poetry package manager installed. You can install it by running `pip install poetry`, or by following instructions in the [Poetry Docs](https://python-poetry.org/docs/#installation)

## Setup

1. Create a `.env` file in the `./backend` directory and set the required environment variables:
HATCHET_CLIENT_TOKEN="<your-hatchet-api-key>"

2. Install the project dependencies:
```
poetry install
```

## Running the API

To start the backend server, run the following command:

```shell
poetry run start-api
```

## Running the Hatchet Worker

In a separate terminal, start the Hatchet worker by running:
```shell
poetry run start-worker
```

## Project Structure

- `src/api/main.py`: FastAPI application setup and endpoints
- `src/workflows/`: Contains Hatchet workflow definitions
  - `scraper_workflow.py`: Main scraper workflow
  - `main.py`: Workflow registration and worker setup

## Workflows

The project contains three main workflows:

1. ScraperWorkflow: Orchestrates the scraping process for both TechCrunch and Google News
2. TechCrunchAIScraperWorkflow: Scrapes AI-related articles from TechCrunch
3. GoogleNewsScraperWorkflow: Scrapes top stories from Google News

These workflows are defined in `src/workflows/scraper_workflow.py` and registered in `src/workflows/main.py`.

## API Endpoints

- `POST /scrape`: Initiates the scraping workflow
- `GET /`: Basic route to confirm the API is working

For more details on the API implementation, refer to `src/api/main.py`.

## Environment Variables

Make sure to set up the following environment variable in your `.env` file:

- `HATCHET_CLIENT_TOKEN`: Your Hatchet API key

## Dependencies

Key dependencies for this project include:

- FastAPI
- Uvicorn
- Hatchet SDK
- Requests
- BeautifulSoup4

For a complete list of dependencies, refer to the `pyproject.toml` file:
```toml
backend/pyproject.toml
```