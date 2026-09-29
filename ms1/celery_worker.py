import os

import requests
from celery import Celery

# Connect to Redis (our message broker)
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
MS2_URL = os.getenv("MS2_URL", "http://ms2:8002")

# Initialize the Celery application
celery_app = Celery("tasks", broker=REDIS_URL)


@celery_app.task
def update_usage_task(client_id: str, operation_name: str):
    """
    This function runs in the background.
    It sends a PUT request to MS2 to update the database.
    """
    payload = {"client_id": client_id, "operation_name": operation_name}
    try:
        requests.put(f"{MS2_URL}/feature/usage/update", json=payload)
    except requests.exceptions.RequestException as e:
        print(f"Failed to update usage for client {client_id}: {e}")
