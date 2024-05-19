from flask import request, abort, Blueprint, jsonify
from data import db_session
from datetime import datetime, timedelta, timezone
from data.users import User
from data.events import Events

from data.event_participants import EventParticip
from sqlalchemy import or_
from flask_jwt_extended import jwt_required, get_jwt_identity


events_blueprint = Blueprint(
    'events',
    __name__,
)


@events_blueprint.route("/events", methods=['GET'])
@jwt_required()
def load_event():
    db_sess = db_session.create_session()
    current_user_id = get_jwt_identity()
    user = db_sess.query(User).filter(User.id == current_user_id).first()
    if not user:
        return jsonify({'success': False, 'error': "User not found"}), 404

    # Retrieve tasks where the current user is either the host or a participant
    events = db_sess.query(Events).filter((Events.host_id == current_user_id) | (Events.participants.any(user_id=current_user_id)) | (user.position == 0)).all()
    event_data = []
    for event in events:
        formatted_cell_date = event.formatted_dates()
        event_particip = []
        for particip in event.participants:
            fio = db_sess.query(User).filter(User.id == particip.user_id).first()
            event_particip.append({
                "id": particip.user_id,
                "label": fio.surname + " " + fio.name + " " + fio.patronymic
            })

        is_participant = current_user_id in event_particip
        host_user = db_sess.query(User).filter(User.id == event.host_id).first()
        host_user_fio = host_user.surname + " " + host_user.name + " " + host_user.patronymic

        event_data.append({
            "id": event.id,
            "event_name": event.event_name,
            "date": formatted_cell_date,
            "host_id": event.host_id,
            "host_name": host_user_fio,
            "description": event.event_descr,
            "is_participant": is_participant,
            "task_particip": event_particip
            })
    db_sess.close()
    return jsonify({'success': True, 'data': event_data})


@events_blueprint.route("/events/add", methods=['POST'])
@jwt_required()
def add_event():
    db_sess = db_session.create_session()
    current_user = get_jwt_identity()
    user = db_sess.query(User).filter(User.id == current_user).first()
    if not user:
        return jsonify({'success': False, 'error': "User not found"}), 404
    new_data = request.json.get('data')
    cell_date = datetime.strptime(new_data.get('date'), '%Y-%m-%d').date() if new_data.get('date')\
        else datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d').date()
    event = Events(
        event_name=new_data.get('event_name'),
        cell_date=cell_date,
        event_descr=new_data.get('description'),
        host_id=current_user,
        time=new_data.get("time")
    )
    db_sess.add(event)
    db_sess.commit()
    event_participants = new_data.get('event_particip')
    for participant in event_participants:
        participant = participant.get("value")
        event_partic = EventParticip(
            event_id=event.id,
            user_id=participant
        )
        db_sess.add(event_partic)
        db_sess.commit()
    db_sess.close()
    return jsonify({'success': True})


@events_blueprint.route("/events/delete", methods=['POST'])
@jwt_required()
def delete_event():
    db_sess = db_session.create_session()
    current_user = get_jwt_identity()
    user = db_sess.query(User).filter(User.id == current_user).first()
    if not user:
        db_sess.close()
        return jsonify({'error': "User not found"}), 404
    new_data = request.json.get('data')
    event_id = new_data.get('id')
    host_id = new_data.get("host_id")
    host_user = db_sess.query(User).filter(User.id == host_id).first()
    event = db_sess.query(Events).filter(Events.id == event_id, or_(Events.host_id == current_user,
                                                              host_user.position >= user.position)).first()
    if event:
        if current_user == event.host_id:
            db_sess.query(EventParticip).filter(EventParticip.event_id == event.id).delete()
            db_sess.delete(event)
        else:
            db_sess.query(EventParticip).filter(EventParticip.event_id == event.id, EventParticip.user_id == current_user).delete()
        db_sess.commit()
        db_sess.close()
    else:
        abort(404)
        db_sess.close()
    return jsonify({'success': True})
