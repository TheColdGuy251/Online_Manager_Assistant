from flask import request, abort, Blueprint, jsonify
from data import db_session
from datetime import datetime, timedelta, timezone
from data.users import User
from data.tasks import Task

from data.task_participants import TaskParticip
from sqlalchemy import or_
from flask_jwt_extended import jwt_required, get_jwt_identity


tasks_blueprint = Blueprint(
    'tasks',
    __name__,
)


@tasks_blueprint.route("/tasks", methods=['GET'])
@jwt_required()
def load_task():
    if request.method == "GET":
        db_sess = db_session.create_session()
        current_user_id = get_jwt_identity()
        user = db_sess.query(User).filter(User.id == current_user_id).first()
        if not user:
            return jsonify({'success': False, 'error': "User not found"}), 404

        # Retrieve tasks where the current user is either the host or a participant
        tasks = db_sess.query(Task).filter((Task.host_id == current_user_id) | (Task.participants.any(user_id=current_user_id)) | (user.position == 0)).all()

        data = []

        for task in tasks:
            formatted_begin_date, formatted_end_date, formatted_date_remind = task.formatted_dates()
            task_particip = []
            for particip in task.participants:
                fio = db_sess.query(User).filter(User.id == particip.user_id).first()
                task_particip.append({
                    "id": particip.user_id,
                    "label": fio.surname + " " + fio.name + " " + fio.patronymic
                })

            is_participant = current_user_id in task_particip
            host_user = db_sess.query(User).filter(User.id == task.host_id).first()
            host_user_fio = host_user.surname + " " + host_user.name + " " +host_user.patronymic
            data.append({
                "id": task.id,
                "task_name": task.task_name,
                "begin_date": formatted_begin_date,
                "end_date": formatted_end_date,
                "condition": task.condition,
                "complete_perc": task.complete_perc,
                "remind": task.remind,
                "date_remind": formatted_date_remind,
                "is_private": task.is_private,
                "priority": task.priority,
                "host_id": task.host_id,
                "host_name": host_user_fio,
                "description": task.description,
                "created_date": task.created_date,
                "is_participant": is_participant,
                "task_particip": task_particip
            })

        return jsonify({'success': True, 'data': data})


@tasks_blueprint.route("/tasks/add", methods=['POST'])
@jwt_required()
def add_task():
    db_sess = db_session.create_session()
    current_user = get_jwt_identity()
    user = db_sess.query(User).filter(User.id == current_user).first()
    if not user:
        return jsonify({'success': False, 'error': "User not found"}), 404
    data = request.json.get('data')
    task = Task(
        task_name=data.get('task_name'),
        begin_date=datetime.strptime(data.get('begin_date'), '%Y-%m-%d').date(),
        end_date=datetime.strptime(data.get('end_date'), '%Y-%m-%d').date(),
        condition=data.get('condition'),
        complete_perc=data.get('complete_perc'),
        remind=bool(data.get('remind')),
        date_remind=datetime.strptime(data.get('date_remind'), '%Y-%m-%d').date(),
        is_private=bool(data.get('is_private')),
        priority=data.get('priority'),
        description=data.get('description'),
        host_id=current_user
    )
    db_sess.add(task)
    db_sess.commit()
    task_participants = data.get('task_particip')
    for participant in task_participants:
        participant = participant.get("value")
        task_partic = TaskParticip(
            task_id=task.id,
            user_id=participant
        )
        db_sess.add(task_partic)
        db_sess.commit()
    return jsonify({'success': True})


@tasks_blueprint.route("/tasks/update", methods=['POST'])
@jwt_required()
def edit_task():
    db_sess = db_session.create_session()
    current_user = get_jwt_identity()
    user = db_sess.query(User).filter(User.id == current_user).first()
    if not user:
        return jsonify({'success': False, 'error': "User not found"}), 404
    data = request.json.get('data')
    task_id = data.get('id')
    host_id = data.get("host_id")
    host_user = db_sess.query(User).filter(User.id == host_id).first()
    task = db_sess.query(Task).filter(Task.id == task_id, or_(Task.host_id == current_user,
                                                              host_user.position < user.position)).first()
    if task:
        task.task_name = data.get('task_name')
        task.begin_date = datetime.strptime(data.get('begin_date'), '%Y-%m-%d').date()
        task.end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
        task.condition = data.get('condition')
        task.complete_perc = data.get('complete_perc')
        task.remind = bool(data.get('remind'))
        task.date_remind = datetime.strptime(data.get('date_remind'), '%Y-%m-%d').date()
        task.is_private = bool(data.get('is_private'))
        task.priority = data.get('priority')
        task.description = data.get('description')
        db_sess.query(TaskParticip).filter(TaskParticip.task_id == task.id).delete()
        task_participants = data.get('task_particip')
        for participant in task_participants:
            participant = participant.get("value")
            task_partic = TaskParticip(
                task_id=task.id,
                user_id=participant
            )
            db_sess.add(task_partic)
            db_sess.commit()

        db_sess.commit()
    return jsonify({'success': True})


@tasks_blueprint.route("/tasks/delete", methods=['POST'])
@jwt_required()
def delete_task():
    db_sess = db_session.create_session()
    current_user = get_jwt_identity()
    user = db_sess.query(User).filter(User.id == current_user).first()
    if not user:
        return jsonify({'error': "User not found"}), 404
    data = request.json.get('data')
    task_id = data.get('id')
    host_id = data.get("host_id")
    host_user = db_sess.query(User).filter(User.id == host_id).first()
    task = db_sess.query(Task).filter(Task.id == task_id, or_(Task.host_id == current_user,
                                                              host_user.position < user.position)).first()
    if task:
        db_sess.query(TaskParticip).filter(TaskParticip.task_id == task.id).delete()
        db_sess.delete(task)
        db_sess.commit()
    else:
        abort(404)
    return jsonify({'success': True})
