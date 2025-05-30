from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from datetime import datetime, UTC
from typing import Optional
from ..db import db


class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str]
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    goal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("goal.id"))
    goal: Mapped[Optional["Goal"]] = relationship(back_populates="tasks")

    @classmethod
    def from_dict(cls, task_data):
        goal_id = task_data.get("goal_id")
        new_task = cls(
            title=task_data["title"],
            description=task_data["description"],
            completed_at=datetime.utcnow() if task_data.get("is_complete") else None,
            goal_id = goal_id
            )

        return new_task

    def to_dict(self):
        task_as_dict = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_complete": bool(self.completed_at),
        }

        if self.goal_id:
            task_as_dict["goal_id"] = self.goal_id

        return task_as_dict


    def mark_complete(self):
        self.completed_at = datetime.now(UTC)

    def mark_incomplete(self):
        self.completed_at = None
