from flask import request, abort, Blueprint, jsonify
from data import db_session
from data.users import User
from data.calendar import Calendar
from sqlalchemy import and_, or_
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import jwt_required, get_jwt_identity

calendar_blueprint = Blueprint(
    'calendar',
    __name__,
)


@calendar_blueprint.route("/calendar", methods=['POST'])
@jwt_required()
def load_calendar():
    db_sess = db_session.create_session()
    current_user_id = get_jwt_identity()
    user = db_sess.query(User).filter(User.id == current_user_id).first()
    if not user:
        db_sess.close()
        return jsonify({'success': False, 'error': "User not found"}), 404
    data = request.json.get('data')
    month = data.get("month")
    year = data.get("year")
    cells = []

    firstweekdayofmonth = datetime(int(year), int(month), 1).weekday()
    if firstweekdayofmonth:
        prevdaysamount = firstweekdayofmonth
    else:
        prevdaysamount = 6
    cellsamount = 42

    for i in range(-prevdaysamount, cellsamount - prevdaysamount):
        firstdayofmonth = datetime(int(year), int(month), 1)
        targetDate = (firstdayofmonth + timedelta(days=i)).strftime('%Y-%m-%d')
        cells.append(
            targetDate.lstrip("0") if len(cells) < 7 else targetDate.lstrip("0")
        )
    first_date = cells[0].split("-")
    last_date = cells[-1].split("-")
    calendar = db_sess.query(Calendar).filter(or_(Calendar.cell_date.like(f'%{first_date[0] + "-" + first_date[1]}%'),
                                                  Calendar.cell_date.like(f'%{last_date[0] + "-" + last_date[1]}%'),
                                                  Calendar.cell_date.like(f'%{year + "-" + month}%')),
                                              Calendar.host_id == current_user_id).all()
    calendar_data = []
    for date in cells:
        events = []
        for calendar_date in calendar:
            if calendar_date.cell_date == date:
                events.append({"name": calendar_date.task_name, "id": calendar_date.task_id})
        calendar_data.append({"id": date, "events": events})
    db_sess.close()
    print(calendar_data)
    return jsonify({'success': True, 'cell_data': calendar_data})


@calendar_blueprint.route("/calendar/add", methods=['POST'])
@jwt_required()
def add_calendar():
    db_sess = db_session.create_session()
    current_user = get_jwt_identity()
    user = db_sess.query(User).filter(User.id == current_user).first()
    if not user:
        db_sess.close()
        return jsonify({'success': False, 'error': "User not found"}), 404
    new_data = request.json.get('data')
    calendar = Calendar(
        task_name=new_data.get("name"),
        task_id=new_data.get("task_id"),
        cell_date=new_data.get('id'),
        host_id=current_user
    )
    existing_task = db_sess.query(Calendar).filter(Calendar.task_id == new_data.get("task_id"),
                                                   Calendar.cell_date == new_data.get('id'),
                                                   Calendar.host_id == current_user).first()
    if existing_task:
        db_sess.close()
        return jsonify({'success': False, 'Error': "Already exists"})
    db_sess.add(calendar)
    db_sess.commit()
    db_sess.close()
    return jsonify({'success': True})


@calendar_blueprint.route("/calendar/delete", methods=['POST'])
@jwt_required()
def delete_calendar():
    db_sess = db_session.create_session()
    current_user = get_jwt_identity()
    user = db_sess.query(User).filter(User.id == current_user).first()
    if not user:
        db_sess.close()
        return jsonify({'error': "User not found"}), 404
    new_data = request.json.get('events')
    cell_date = new_data.get('id')
    task_id = new_data.get('task_id')
    calendar = db_sess.query(Calendar).filter(and_(Calendar.cell_date == cell_date, Calendar.host_id == current_user,
                                                   Calendar.task_id == task_id)).first()

    if calendar:
        db_sess.delete(calendar)
        db_sess.commit()
    else:
        abort(404)
    db_sess.close()
    return jsonify({'success': True})
