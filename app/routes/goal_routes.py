from flask import Blueprint, abort, make_response, request, Response
from app.models.goal import Goal
from app.models.task import Task
from .route_utilities import validate_model
from ..db import db

goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

@goals_bp.post("")
def create_goal():
    request_body = request.get_json()

    try:
        new_goal = Goal.from_dict(request_body)

    except KeyError:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))

    db.session.add(new_goal)
    db.session.commit()

    return {"goal": new_goal.to_dict()}, 201

@goals_bp.get("")
def get_all_goals():
    query = db.select(Goal)

    title_param = request.args.get("title")
    if title_param:
        query = query.where(Goal.name.ilike(f"%{title_param}%"))

    goals = db.session.scalars(query)
    goals_response = []
    for goal in goals:
        goals_response.append(goal.to_dict())

    return goals_response


@goals_bp.get("/<goal_id>")
def get_one_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    return {"goal": goal.to_dict()}


@goals_bp.put("/<goal_id>")
def update_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()

    goal.title = request_body["title"]
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@goals_bp.delete("/<goal_id>")
def delete_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    db.session.delete(goal)
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@goals_bp.post("/<goal_id>/tasks")
def post_task_ids_to_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    request_body = request.get_json()
    task_ids = request_body.get("task_ids", [])
    goal.tasks = []

    for task_id in task_ids:
        task = validate_model(Task, task_id)
        goal.tasks.append(task) 

    db.session.commit()

    return {"id": goal.id, "task_ids": task_ids}, 200


@goals_bp.get("/<goal_id>/tasks")
def get_tasks_for_one_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    task_list = [task.to_dict() for task in goal.tasks]

    response = {
        "id": goal.id,
        "title": goal.title,
        "tasks": task_list
    }
    return response, 200
