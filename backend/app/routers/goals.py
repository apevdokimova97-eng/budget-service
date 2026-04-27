from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/goals", tags=["Goals"])


def goal_to_response(goal: models.Goal):
    progress = 0

    if goal.target_amount > 0:
        progress = round((goal.current_amount / goal.target_amount) * 100, 2)

    return {
        "id": goal.id,
        "title": goal.title,
        "target_amount": goal.target_amount,
        "current_amount": goal.current_amount,
        "currency": goal.currency,
        "deadline": goal.deadline,
        "progress_percent": progress,
    }


@router.post("/", response_model=schemas.GoalResponse)
def create_goal(
    goal: schemas.GoalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if goal.target_amount <= 0:
        raise HTTPException(status_code=400, detail="target_amount must be greater than 0")

    if goal.current_amount < 0:
        raise HTTPException(status_code=400, detail="current_amount cannot be negative")

    new_goal = models.Goal(
        user_id=current_user.id,
        title=goal.title,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        currency=goal.currency,
        deadline=goal.deadline,
    )

    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)

    return goal_to_response(new_goal)


@router.get("/", response_model=list[schemas.GoalResponse])
def get_goals(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    goals = db.query(models.Goal).filter(
        models.Goal.user_id == current_user.id
    ).order_by(models.Goal.id.desc()).all()

    return [goal_to_response(goal) for goal in goals]


@router.put("/{goal_id}", response_model=schemas.GoalResponse)
def update_goal(
    goal_id: int,
    goal_data: schemas.GoalUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id,
    ).first()

    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    update_data = goal_data.model_dump(exclude_unset=True)

    if "target_amount" in update_data and update_data["target_amount"] <= 0:
        raise HTTPException(status_code=400, detail="target_amount must be greater than 0")

    if "current_amount" in update_data and update_data["current_amount"] < 0:
        raise HTTPException(status_code=400, detail="current_amount cannot be negative")

    for field, value in update_data.items():
        setattr(goal, field, value)

    db.commit()
    db.refresh(goal)

    return goal_to_response(goal)


@router.delete("/{goal_id}")
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id,
    ).first()

    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    db.delete(goal)
    db.commit()

    return {"message": "Goal deleted"}


@router.post("/{goal_id}/contributions", response_model=schemas.GoalContributionResponse)
def add_goal_contribution(
    goal_id: int,
    contribution: schemas.GoalContributionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id,
    ).first()

    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    if contribution.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be greater than 0")

    new_contribution = models.GoalContribution(
        user_id=current_user.id,
        goal_id=goal.id,
        amount=contribution.amount,
        currency=contribution.currency,
        comment=contribution.comment,
    )

    goal.current_amount += contribution.amount

    db.add(new_contribution)
    db.commit()
    db.refresh(new_contribution)

    return new_contribution


@router.get("/{goal_id}/contributions", response_model=list[schemas.GoalContributionResponse])
def get_goal_contributions(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id,
    ).first()

    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    return db.query(models.GoalContribution).filter(
        models.GoalContribution.goal_id == goal_id,
        models.GoalContribution.user_id == current_user.id,
    ).order_by(models.GoalContribution.date.desc()).all()


@router.delete("/contributions/{contribution_id}")
def delete_goal_contribution(
    contribution_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    contribution = db.query(models.GoalContribution).filter(
        models.GoalContribution.id == contribution_id,
        models.GoalContribution.user_id == current_user.id,
    ).first()

    if not contribution:
        raise HTTPException(status_code=404, detail="Contribution not found")

    goal = db.query(models.Goal).filter(
        models.Goal.id == contribution.goal_id,
        models.Goal.user_id == current_user.id,
    ).first()

    if goal:
        goal.current_amount = max(0, goal.current_amount - contribution.amount)

    db.delete(contribution)
    db.commit()

    return {"message": "Contribution deleted"}