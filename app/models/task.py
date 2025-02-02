from flask import current_app
from app import db
import os
import requests
from datetime import datetime, timezone


class Task(db.Model):
    """This is a model that corresponds to the task table in the database
    Attrributes:
        - id: generated automatically, int
        - title: must be provided, string
        - description: must be provided, string
        - completed_at: must be provided; datetime or None/null
        - goal_id: foreign key corresponding to goal.id
        - goals: establishes relationship between task and goal tables
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey("goal.id"))
    goal = db.relationship("Goal", back_populates="tasks")

    def to_dict(self):
        """This is a method that returns a dictionary of the object's attributes"""
        is_complete = False if not self.completed_at else True

        response = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_complete": is_complete,
        }

        if self.goal:
            response["goal_id"] = self.goal_id

        return response

    def update(self, task_dict):
        """This is a method that updates the object's title and description attributes"""
        self.title = task_dict["title"]
        self.description = task_dict["description"]

        if "completed_at" in task_dict:
            self.completed_at = task_dict["completed_at"]

        return self

    def notify_slack_bot(self):
        """This is a method to send a post request to the slack api with the name of a specified task"""
        SLACK_API_KEY = os.environ.get("SLACK_API_KEY")

        req_body = {
            "channel": "task-notifications",
            "text": f"Someone just completed the task {self.title}"
        }

        headers = {
            "Authorization": f"Bearer {SLACK_API_KEY}"
        }

        path = "https://slack.com/api/chat.postMessage"

        requests.post(path, json=req_body, headers=headers)

    def mark_complete(self):
        """This is a method to mark a task complete"""
        self.completed_at = datetime.now(timezone.utc)
        self.notify_slack_bot()
        return self

    def mark_incomplete(self):
        """This is a method to mark a task incomplete"""
        self.completed_at = None
        return self

    @classmethod
    def new_from_dict(cls, task_dict):
        """This is a method to create a new task object from a dictionary of attributes"""
        return cls(
            title=task_dict["title"],
            description=task_dict["description"],
            completed_at=task_dict["completed_at"]
        )
