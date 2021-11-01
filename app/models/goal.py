from flask import current_app
from app import db
from app.routes.route_utils import is_valid_int


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task", back_populates="goal")

    def to_dict(self, include_tasks=False):
        response = {
            "id": self.id,
            "title": self.title,
        }

        if include_tasks:
            response["tasks"] = [task.to_dict() for task in self.tasks]

        return response

    def to_basic_dict(self):
        response = {
            "id": self.id
        }

        if self.tasks:
            response["task_ids"] = [task.id for task in self.tasks]

        return response

    def update(self, goal_dict):
        self.title = goal_dict["title"]
        return self

    @classmethod
    def new_from_dict(cls, goal_dict):
        return cls(
            title=goal_dict["title"]
        )

    @classmethod
    def get_by_id(cls, id):
        """Grab one goal from the database by id and return it"""
        is_valid_int(id)
        return cls.query.get_or_404(id)
