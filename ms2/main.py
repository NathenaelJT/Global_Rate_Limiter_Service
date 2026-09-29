import models
from database import engine, get_db
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Create the database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Microservice 2 - Rate Limiter Engine")


# Data formats for receiving requests
class UsageUpdateReq(BaseModel):
    client_id: str
    operation_name: str


class StatusUpdateReq(BaseModel):
    client_id: str
    usage_limit_exceeded: bool


MAX_REQUESTS = 1000


@app.put("/feature/usage/update")
def update_usage(req: UsageUpdateReq, db: Session = Depends(get_db)):
    """
    Records that a client used a feature.
    If they hit 1000 requests, we lock their account by setting it to True.
    """
    # 1. Add a new usage record to Table 1
    new_usage = models.Usage(
        client_id=req.client_id, feature_name=req.operation_name
    )
    db.add(new_usage)
    db.commit()

    # 2. Count total usage for this client
    count = (
        db.query(models.Usage)
        .filter(models.Usage.client_id == req.client_id)
        .count()
    )

    # 3. If they exceeded the limit, update Table 2
    if count >= MAX_REQUESTS:
        status = (
            db.query(models.ClientStatus)
            .filter(models.ClientStatus.client_id == req.client_id)
            .first()
        )
        if not status:
            status = models.ClientStatus(
                client_id=req.client_id, usage_limit_exceeded=True
            )
            db.add(status)
        else:
            status.usage_limit_exceeded = True
        db.commit()

    return {"message": "Usage updated successfully", "current_count": count}


@app.post("/status/update/")
def update_status(req: StatusUpdateReq, db: Session = Depends(get_db)):
    """
    Allows overriding or manually setting if a client is blocked.
    """
    status = (
        db.query(models.ClientStatus)
        .filter(models.ClientStatus.client_id == req.client_id)
        .first()
    )
    if not status:
        status = models.ClientStatus(
            client_id=req.client_id,
            usage_limit_exceeded=req.usage_limit_exceeded,
        )
        db.add(status)
    else:
        status.usage_limit_exceeded = req.usage_limit_exceeded
    db.commit()
    return {"message": "Status updated successfully"}


@app.get("/status/get")
def get_status(client_id: str, db: Session = Depends(get_db)):
    """
    Returns whether the client is allowed to use the service.
    """
    status = (
        db.query(models.ClientStatus)
        .filter(models.ClientStatus.client_id == client_id)
        .first()
    )

    if not status:
        # If no status exists yet, they haven't exceeded any limits
        return {"client_id": client_id, "usage_limit_exceeded": False}

    return {
        "client_id": client_id,
        "usage_limit_exceeded": status.usage_limit_exceeded,
    }
