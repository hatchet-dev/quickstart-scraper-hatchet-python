import json
import logging
import os
from typing import AsyncGenerator
import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from hatchet_sdk import Hatchet
from pydantic import BaseModel

from ..config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set the environment variable for Hatchet
os.environ["HATCHET_CLIENT_TOKEN"] = settings.hatchet_client_token

# Initialize Hatchet client
hatchet = Hatchet()

# Initialize FastAPI app
app = FastAPI()

# Define CORS origins
origins = [
    "http://localhost:3000",
    "localhost:3000"
]

# Apply CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Define Pydantic model for response
class ScrapeResponse(BaseModel):
    messageId: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Hatchet Scraper API!"}

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape():
    workflowRun = await hatchet.client.admin.aio.run_workflow("ScraperWorkflow", {})
    logger.info(f"Started scraping workflow with ID: {workflowRun.workflow_run_id}")
    return ScrapeResponse(messageId=workflowRun.workflow_run_id)

# Generator function to stream events from a Hatchet workflow
async def event_stream_generator(workflowRunId):
    logger.info(f"Starting event stream for workflow run ID: {workflowRunId}")
    workflowRun = hatchet.client.admin.get_workflow_run(workflowRunId)

    try:
        async for event in workflowRun.stream():
            logger.info(f"Received event: {event.type}")
            data = json.dumps({
                "type": event.type,
                "payload": event.payload,
                "messageId": workflowRunId
            })
            yield f"data: {data}\n\n"

        result = await workflowRun.result()
        logger.info(f"Workflow completed. Result: {result}")
        data = json.dumps({
            "type": "result",
            "payload": result,
            "messageId": workflowRunId
        })
        yield f"data: {data}\n\n"
    except Exception as e:
        logger.error(f"Error in event stream: {str(e)}")
        error_data = json.dumps({
            "type": "error",
            "payload": {"message": str(e)},
            "messageId": workflowRunId
        })
        yield f"data: {error_data}\n\n"

@app.get("/message/{messageId}")
async def stream(messageId: str):
    return StreamingResponse(event_stream_generator(messageId), media_type='text/event-stream')

def start():
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    start()