from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from dependencies.database import get_db
from models.changelog import ChangeLog
from schemas.changelog import ChangeLog as ChangeLogSchema
from schemas.error import Error

router = APIRouter()

@router.get(
    "/",
    response_model=List[ChangeLogSchema],
    summary="List change logs",
    description="Retrieves a paginated list of change logs for auditing purposes.",
    operation_id="list_change_logs",
    responses={
        200: {"description": "List of change logs", "model": List[ChangeLogSchema]},
        429: {"description": "Rate limit exceeded", "model": Error}
    }
)
def list_change_logs(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    skip = (page - 1) * limit
    return db.query(ChangeLog).offset(skip).limit(limit).all()
