from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User, UserInteraction
from app.schemas import FeedbackCreate, FeedbackResponse


def get_or_create_demo_user(db: Session, user_id: int) -> User:
    user = db.scalar(select(User).where(User.user_id == user_id))
    if user is None:
        user = User(user_id=user_id, username="xiaozhihuang", age=24)
        db.add(user)
        db.commit()
        db.refresh(user)
    elif user_id == 1 and user.username != "xiaozhihuang":
        user.username = "xiaozhihuang"
        db.commit()
        db.refresh(user)
    return user


def record_feedback(db: Session, payload: FeedbackCreate) -> FeedbackResponse:
    interaction = UserInteraction(
        user_id=payload.user_id,
        song_id=payload.song_id,
        action=payload.action,
        liked=payload.action.value == "like",
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return FeedbackResponse(interaction_id=interaction.interaction_id, action=interaction.action, timestamp=interaction.timestamp)
