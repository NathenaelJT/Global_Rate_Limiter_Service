import os
import redis
import requests
from celery_worker import update_usage_task
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Microservice 1 - Calculator")

# We use an environment variable to find MS2. In Docker, it's called 'ms2'
MS2_URL = os.getenv("MS2_URL", "http://ms2:8002")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

redis_client = redis.from_url(REDIS_URL)
MAX_REQUESTS = 1000


# Data format for our endpoints
class MathRequest(BaseModel):
    client_id: str
    num1: float
    num2: float


def check_client_status(client_id: str):
    """
    Helper function to ask MS2 if the client is allowed to make a request.
    """
    # 1. Fast, real-time check using Redis to prevent race conditions
    current_count = redis_client.get(f"usage_count:{client_id}")
    if current_count and int(current_count) >= MAX_REQUESTS:
        raise HTTPException(
            status_code=403,
            detail="Usage limit exceeded. You have made too many requests.",
        )

    # 2. Ask MS2 for status (for persistent blocks)
    try:
        response = requests.get(
            f"{MS2_URL}/status/get", params={"client_id": client_id}
        )
        response.raise_for_status()
        data = response.json()

        if data.get("usage_limit_exceeded"):
            raise HTTPException(
                status_code=403,
                detail="Usage limit exceeded. "
                "You have made too many requests.",
            )

    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=500,
            detail="Error communicating with Rate Limiter Service",
        )


@app.post("/add")
def add_numbers(req: MathRequest):
    # 1. Check if allowed
    check_client_status(req.client_id)

    # 2. Do the math
    result = req.num1 + req.num2

    # Increment our fast Redis counter
    redis_client.incr(f"usage_count:{req.client_id}")

    # 3. Trigger the background job to update usage in MS2
    update_usage_task.delay(req.client_id, "add")

    return {"result": result}


@app.post("/subtract")
def subtract_numbers(req: MathRequest):
    # 1. Check if allowed
    check_client_status(req.client_id)

    # 2. Do the math
    result = req.num1 - req.num2

    # Increment our fast Redis counter
    redis_client.incr(f"usage_count:{req.client_id}")

    # 3. Trigger the background job
    update_usage_task.delay(req.client_id, "subtract")

    return {"result": result}
