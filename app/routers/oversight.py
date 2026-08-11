import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import DecisionRecord

router = APIRouter(prefix="/api/v1/oversight", tags=["Governance"])


class ReviewRequest(BaseModel):
    reason: str


@router.post("/{decision_id}/approve")
def approve_decision(
    decision_id: str, req: ReviewRequest, db: Session = Depends(get_db)
):
    decision = (
        db.query(DecisionRecord)
        .filter(DecisionRecord.decision_id == decision_id)
        .first()
    )
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    if decision.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail="Only pending decisions can be reviewed. Create a new event to override.",
        )

    decision.status = "APPROVED"
    decision.reason = req.reason
    decision.reviewed_at = datetime.utcnow()
    decision.reviewed_by = "current_user"  # To be integrated with Auth dependency

    db.commit()
    db.refresh(decision)
    return decision


@router.post("/{decision_id}/reject")
def reject_decision(
    decision_id: str, req: ReviewRequest, db: Session = Depends(get_db)
):
    decision = (
        db.query(DecisionRecord)
        .filter(DecisionRecord.decision_id == decision_id)
        .first()
    )
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    if decision.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail="Only pending decisions can be reviewed. Create a new event to override.",
        )

    decision.status = "REJECTED"
    decision.reason = req.reason
    decision.reviewed_at = datetime.utcnow()
    decision.reviewed_by = "current_user"  # To be integrated with Auth dependency

    db.commit()
    db.refresh(decision)
    return decision


@router.get("/history")
def get_history(db: Session = Depends(get_db)):
    return (
        db.query(DecisionRecord)
        .order_by(DecisionRecord.created_at.desc())
        .limit(50)
        .all()
    )


class CreateDecisionRequest(BaseModel):
    event_id: str
    recommendation: str
    recommended_action: str
    simulation_id: str


@router.post("/")
def create_decision(req: CreateDecisionRequest, db: Session = Depends(get_db)):
    record = DecisionRecord(
        decision_id=str(uuid.uuid4()),
        event_id=req.event_id,
        recommendation=req.recommendation,
        recommended_action=req.recommended_action,
        simulation_id=req.simulation_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
