from flask import Blueprint, abort, make_response, request, Response
from app.models.task import Task
from .route_utilities import validate_model, chat_post_message
from sqlalchemy import asc, desc
from ..db import db

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.post("")
def create_task():
    request_body = request.get_json()

    try:
        new_task = Task.from_dict(request_body)

    except KeyError as error:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))

    db.session.add(new_task)
    db.session.commit()

    return {"task": new_task.to_dict()}, 201

@tasks_bp.get("")
def get_all_tasks():
    query = db.select(Task)
    
    title_param = request.args.get("title")
    if title_param:
        query = query.where(Task.title.ilike(f"%{title_param}%"))

    sort_param = request.args.get("sort")
    if sort_param:
        if sort_param.lower() == "asc":
            query = query.order_by(asc(Task.title))
        elif sort_param.lower() == "desc":
            query = query.order_by(desc(Task.title))

    query = query.order_by(Task.id)

    tasks = db.session.scalars(query)

    tasks_response = []
    for task in tasks:
        tasks_response.append(task.to_dict())
    return tasks_response


@tasks_bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_model(Task, task_id)

    return {"task": task.to_dict()}


@tasks_bp.put("/<task_id>")
def update_task(task_id):
    task = validate_model(Task, task_id)
    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@tasks_bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_model(Task, task_id)
    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@tasks_bp.patch("/<task_id>/mark_complete")
def mark_task_complete(task_id):
    task = validate_model(Task, task_id)
    task.mark_complete()
    db.session.commit()

    #chat_post_message(task)

    return Response(status=204, mimetype="application/json")

@tasks_bp.patch("/<task_id>/mark_incomplete")
def mark_task_incomplete(task_id):
    task = validate_model(Task, task_id)

    task.mark_incomplete()
    db.session.commit()

    return Response(status=204, mimetype="application/json")