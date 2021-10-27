from flask import Blueprint, jsonify, request, abort
from app import db
from app.models.task import Task
from datetime import datetime, timezone

task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


def is_valid_int(number):
    try:
        int(number)
    except:
        abort(400)


def get_task_by_id(id):
    is_valid_int(id)
    return Task.query.get_or_404(id)


@task_bp.route("", methods=["GET"])
def read_tasks():
    sort_query = request.args.get("sort")
    if sort_query == 'asc':
        tasks = Task.query.order_by(Task.title).all()
    elif sort_query == 'desc':
        tasks = Task.query.order_by(Task.title.desc()).all()
    else:
        tasks = Task.query.all()
    tasks = [task.to_dict() for task in tasks]
    return jsonify(tasks), 200


@task_bp.route("", methods=["POST"])
def create_task():
    req = request.get_json()

    try:
        new_task = Task(
            title=req["title"], description=req["description"], completed_at=req["completed_at"])
    except:
        return jsonify({"details": "Invalid data"}), 400

    db.session.add(new_task)
    db.session.commit()

    return jsonify({"task": new_task.to_dict()}), 201


@task_bp.route("/<id>", methods=["GET"])
def read_task(id):
    task = get_task_by_id(id)
    return jsonify({"task": task.to_dict()}), 200


@task_bp.route("/<id>", methods=["PUT"])
def update_task(id):
    task = get_task_by_id(id)
    req = request.get_json()

    task.title = req["title"]
    task.description = req["description"]

    db.session.commit()
    return jsonify({"task": task.to_dict()}), 200


@task_bp.route("/<id>", methods=["DELETE"])
def delete_task(id):
    task = get_task_by_id(id)
    db.session.delete(task)
    db.session.commit()

    response_body = {
        "details": f'Task {task.id} "{task.title}" successfully deleted'
    }
    return jsonify(response_body), 200


@task_bp.route("/<id>/mark_complete", methods=["PATCH"])
def mark_complete(id):
    task = get_task_by_id(id)
    task.completed_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"task": task.to_dict()}), 200


@task_bp.route("/<id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete(id):
    task = get_task_by_id(id)
    task.completed_at = None
    db.session.commit()
    return jsonify({"task": task.to_dict()}), 200
