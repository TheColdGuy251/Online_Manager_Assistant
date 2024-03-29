from flask import Flask, render_template, redirect, request, make_response, session, abort, jsonify, url_for, \
    send_from_directory
from data import db_session
from datetime import datetime, timedelta, timezone
from data.users import User
from data.tasks import Task
from data.calendar import Calendar
from sqlalchemy import text
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, jwt_manager, get_jwt, set_access_cookies, unset_jwt_cookies

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tyuiu_secret_key'
CORS(app)
jwt = JWTManager(app)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=14)


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
    return jsonify({'success': "OK"})


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


@app.route("/tasks", methods=['GET'])
@jwt_required()
def load_task():
    if request.method == "GET":
        db_sess = db_session.create_session()
        current_user = get_jwt_identity()
        user = db_sess.query(User).filter(User.id == current_user).first()
        if not user:
            return jsonify({'error': "User not found"}), 404
        tasks = db_sess.query(Task).filter(Task.host_id == user.id).all()
        data = {}
        for i, task in enumerate(tasks):
            data[i] = {
                "task_name": task.task_name,
                "begin_date": task.begin_date,
                "end_date": task.end_date,
                "condition": task.condition,
                "complete_perc": task.complete_perc,
                "remind": task.remind,
                "date_remind": task.date_remind,
                "is_private": task.is_private,
                "priority": task.priority,
                "host_id": task.host_id,
                "description": task.description,
                "created_date": task.created_date
            }
        return jsonify({'success': True, 'data': data})


@app.route("/tasks/add", methods=['POST'])
@jwt_required()
def addtask():
    db_sess = db_session.create_session()
    current_user = get_jwt_identity()
    user = db_sess.query(User).filter(User.id == current_user).first()
    if not user:
        return jsonify({'error': "User not found"}), 404
    data = request.json.get('data')
    task = Task(
        task_name=data.get('task_name'),
        begin_date=datetime.strptime(data.get('begin_date'), '%d.%m.%Y').date(),
        end_date=datetime.strptime(data.get('end_date'), '%d.%m.%Y').date(),
        condition=data.get('condition'),
        complete_perc=data.get('complete_perc'),
        remind=bool(data.get('remind')),
        date_remind=datetime.strptime(data.get('date_remind'), '%d.%m.%Y').date(),
        is_private=bool(data.get('is_private')),
        priority=data.get('priority'),
        description=data.get('description'),
        host_id=current_user
    )
    db_sess.add(task)
    db_sess.commit()
    return jsonify({'success': True})


@app.route("/calendar", methods=['GET'])
@jwt_required()
def load_calendar():
    if request.method == "GET":
        db_sess = db_session.create_session()
        current_user = get_jwt_identity()
        user = db_sess.query(User).filter(User.id == current_user).first()
        if not user:
            return jsonify({'error': "User not found"}), 404
        calendar = db_sess.query(Calendar).filter(Calendar.host_id == user.id).all()
        data = {}
        for i, task in enumerate(calendar):
            data[i] = {
                "task_name": task.task_name,
                "begin_date": task.begin_date,
                "end_date": task.end_date,
                "is_private": task.is_private,
                "host_id": task.host_id,
            }
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


# регистрация аккаунта
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    if request.method == "POST":
        db_sess = db_session.create_session()
        data = request.json.get('data')
        username = data.get('username')
        surname = data.get('surname')
        name = data.get('name')
        patronymic = data.get('patronymic')
        about = data.get('about')
        email = data.get('email')
        password = data.get('password')
        if db_sess.query(User).filter(User.username == username).first():
            return {'success': False, 'Error': 'user_exists'}
        if db_sess.query(User).filter(User.email == email).first():
            return {'success': False, 'Error': 'email_exists'}
        user = User(
            username=username,
            surname=surname,
            name=name,
            patronymic=patronymic,
            email=email,
            about=about
        )
        user.set_password(password)
        db_sess.add(user)
        db_sess.commit()
        access_token = create_access_token(identity=user.id)
        return jsonify({'success': True, 'access_token': access_token})


# вход в аккаунт
@app.route('/login', methods=['GET', 'POST'])
def login():
    data = request.json.get('data')
    email = data.get('email')
    password = data.get('password')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == email).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token, "login": user.username}), 200
    return jsonify({'success': False, "Error": "WrongAuth"})


@app.route("/logout", methods=["POST"])
def logout():
    unset_jwt_cookies(jsonify({"Success": True}))
    return jsonify({"Success": True})


# переход в профиль
@app.route("/profile/<string:username>", methods=['GET'])
def profile(username):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(username=username).first()

    if user:
        user_dict = {'username': user.username, 'surname': user.surname, 'name': user.name,
                     'patronymic': user.patronymic, 'about': user.about, 'email': user.email,
                     'created_date': user.created_date}
        return jsonify({'data': user_dict})
    return jsonify({'data': 'User not found'})


# изменение профиля
@app.route("/profile/<string:username>/edit", methods=['GET', 'POST'])
@jwt_required()
def profile_edit(username):
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == username).first()
        if user:
            user_dict = {'username': user.username, 'surname': user.surname, 'name': user.name,
                         'patronymic': user.patronymic, 'about': user.about, 'email': user.email,
                         'created_date': user.created_date}
            return jsonify({'data': user_dict})
        else:
            jsonify({'data': 'User not found'})
    if request.method == "POST":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == username).first()
        if user:
            data = request.json.get('data')
            user.username = data.get('username')
            user.surname = data.get('surname')
            user.name = data.form.get('name')
            user.patronymic = data.get('patronymic')
            user.about = data.get('about')
            user.email = data.get('email')
            password = data.get('password')
            if db_sess.query(User).filter(User.username == user.username).first():
                return {'success': 'user_exists'}
            if db_sess.query(User).filter(User.email == user.email).first():
                return {'success': 'email_exists'}
            user.set_password(password)

            db_sess.commit()
            return jsonify({'success': "OK"})
        else:
            return jsonify({'data': 'User not found'})
    return jsonify({'success': "OK"})


# удаление профиля
@app.route("/profile/<string:username>/delete", methods=['GET', 'POST'])
@jwt_required()
def profile_delete(username):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(username=username).first()
    if user:
        db_sess.delete(user)
        db_sess.commit()
    else:
        return jsonify({'success': False, 'Error': 'User not found'})
    return jsonify({'success': True})


if __name__ == '__main__':
    main()
