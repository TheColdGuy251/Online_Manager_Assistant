from flask import Flask, request, make_response, jsonify
from data import db_session
from datetime import datetime, timedelta, timezone
from data.users import User
from data.tasks import Task
from data.calendar import Calendar
from contacts import contact_blueprint
from tasks import tasks_blueprint
from auth import auth_blueprint
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt,\
    set_access_cookies

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tyuiu_secret_key'
CORS(app)
jwt = JWTManager(app)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=14)

app.config['SQLALCHEMY_POOL_SIZE'] = 20
app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600
app.register_blueprint(contact_blueprint)
app.register_blueprint(tasks_blueprint)
app.register_blueprint(auth_blueprint)

def main():
    db_session.global_init("db/users.db")
    app.run()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.route("/", methods=['GET', 'POST'])
def index():
    return jsonify({'success': True})


@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response


def get_user_by_id(db_sess, user_id):
    """Helper function to get a user by ID."""
    return db_sess.get(User, user_id)


def get_current_user(db_sess, current_user_id):
    """Helper function to get the current user."""
    return get_user_by_id(db_sess, current_user_id)


def get_contact_details(db_sess, contact, current_user_id):
    """Helper function to get contact details."""
    other_user_id = contact.receiver_id if contact.sender_id == current_user_id else contact.sender_id
    other_user = get_user_by_id(db_sess, other_user_id)
    if other_user:
        return {
            "id": other_user.id,
            "username": other_user.username,
            "surname": other_user.surname,
            "name": other_user.name,
            "patronymic": other_user.patronymic,
            "email": other_user.email,
            "about": other_user.about,
        }
    return None


@app.route("/calendar", methods=['GET'])
@jwt_required()
def load_calendar():
    db_sess = db_session.create_session()
    current_user_id = get_jwt_identity()
    user = db_sess.query(User).filter(User.id == current_user_id).first()
    if not user:
        return jsonify({'success': False, 'error': "User not found"}), 404

    # Retrieve tasks where the current user is either the host or a participant
    tasks = db_sess.query(Task).filter(
        (Task.host_id == current_user_id) | (Task.participants.any(user_id=current_user_id))).all()

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
            "description": task.description,
            "created_date": task.created_date,
            "is_participant": is_participant,
            "task_particip": task_particip
        })

    return jsonify({'success': True, 'data': data})


@app.route("/calendar/add", methods=['POST'])
@jwt_required()
def add_calendar():
    db_sess = db_session.create_session()
    current_user = get_jwt_identity()
    user = db_sess.query(User).filter(User.id == current_user).first()
    task = db_sess.query(Task).filter(Task.host_id == current_user).first()
    if not user:
        return jsonify({'error': "User not found"}), 404
    data = request.json.get('data')
    calendar = Calendar(
        task_name=task.task_name,
        begin_date=datetime.strptime(data.get('begin_date'), '%d.%m.%Y').date(),
        end_date=datetime.strptime(data.get('end_date'), '%d.%m.%Y').date(),
        is_private=bool(data.get('is_private')),
        host_id=current_user
    )
    db_sess.add(calendar)
    db_sess.commit()
    return jsonify({'success': True})


if __name__ == '__main__':
    main()
