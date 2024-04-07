from flask import Flask, render_template, redirect, request, make_response, session, abort, jsonify, url_for, \
    send_from_directory
from data import db_session
from datetime import datetime, timedelta, timezone
from data.users import User
from data.tasks import Task
from data.friends import Friends
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


@app.route("/tasks", methods=['GET'])
@jwt_required()
def load_task():
    if request.method == "GET":
        db_sess = db_session.create_session()
        current_user = get_jwt_identity()
        user = db_sess.query(User).filter(User.id == current_user).first()
        if not user:
            return jsonify({'success': False, 'error': "User not found"}), 404
        tasks = db_sess.query(Task).filter(Task.host_id == user.id).all()
        data = []
        for task in tasks:
            formatted_begin_date, formatted_end_date, formatted_date_remind = task.formatted_dates()
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
                "created_date": task.created_date
            })
        print(task)
        return jsonify({'success': True, 'data': data})


@app.route("/tasks/add", methods=['POST'])
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


@app.route("/tasks/update", methods=['POST'])
@jwt_required()
def edit_task():
    db_sess = db_session.create_session()
    current_user = get_jwt_identity()
    user = db_sess.query(User).filter(User.id == current_user).first()
    if not user:
        return jsonify({'success': False, 'error': "User not found"}), 404
    data = request.json.get('data')
    task_id = data.get('id')
    task = db_sess.query(Task).filter(Task.id == task_id, Task.host_id == current_user).first()
    if task:
        task.task_name = data.get('task_name')
        task.begin_date = datetime.strptime(data.get('begin_date'), '%d.%m.%Y').date()
        task.end_date = datetime.strptime(data.get('end_date'), '%d.%m.%Y').date()
        task.condition = data.get('condition')
        task.complete_perc = data.get('complete_perc')
        task.remind = bool(data.get('remind'))
        task.date_remind = datetime.strptime(data.get('date_remind'), '%d.%m.%Y').date()
        task.is_private = bool(data.get('is_private'))
        task.priority = data.get('priority')
        task.description = data.get('description')
        db_sess.commit()
    return jsonify({'success': True})


@app.route("/tasks/delete", methods=['POST'])
@jwt_required()
def delete_task():
    db_sess = db_session.create_session()
    current_user = get_jwt_identity()
    user = db_sess.query(User).filter(User.id == current_user).first()
    if not user:
        return jsonify({'error': "User not found"}), 404
    data = request.json.get('data')
    task_id = data.get('task_id')
    task = db_sess.query(Task).filter(Task.id == task_id, Task.host_id == current_user).first()
    if task:
        db_sess.delete(task)
        db_sess.commit()
    else:
        abort(404)
    return jsonify({'success': True})


@app.route("/calendar", methods=['GET'])
@jwt_required()
def load_calendar():
    if request.method == "GET":
        db_sess = db_session.create_session()
        current_user = get_jwt_identity()
        user = db_sess.query(User).filter(User.id == current_user).first()
        if not user:
            return jsonify({'success': False, 'error': "User not found"}), 404
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

"""
@app.route("/contacts", methods=['GET'])
@jwt_required()
def load_contacts():
    if request.method == "GET":
        db_sess = db_session.create_session()
        current_user = get_jwt_identity()
        user = db_sess.query(User).filter(User.id == current_user).first()
        if not user:
            return jsonify({'error': "User not found"}), 404
        contacts = db_sess.query(Friends).filter(Friends.user_id == user.id,
                                                 Friends.confirmed).all()
        data = []
        for contact in contacts:

            data.append({
                "id": contact.id,
                "username": contact.username,
                "surname": contact.surname,
                "name": contact.name,
                "patronymic": contact.patronymic,
                "about": contact.about,
            })
        return jsonify({'success': True, 'data': data})
"""

@app.route("/contacts/find", methods=['POST'])
@jwt_required()
def load_contacts():
    if request.method == "GET":
        db_sess = db_session.create_session()
        current_user = get_jwt_identity()
        user = db_sess.query(User).filter(User.id == current_user).first()
        data = request.json.get('data')
        username = data.get('username')
        if not user:
            return jsonify({'success': False, 'error': "User not found"}), 404
        users = db_sess.query(User).filter(username in User.username).all()
        data = {}
        for i, user in enumerate(users):
            data[i] = {
                "id": users.id,
                "username": users.username,
                "surname": users.surname,
                "name": users.name,
                "patronymic": users.patronymic,
                "about": users.about,
            }
        return jsonify({'success': True, 'data': data})


"""

@app.route("/contacts/requests", methods=['GET'])
@jwt_required()
def load_contacts():
    if request.method == "GET":
        db_sess = db_session.create_session()
        current_user = get_jwt_identity()
        user = db_sess.query(User).filter(User.id == current_user).first()
        if not user:
            return jsonify({'error': "User not found"}), 404
        contacts = db_sess.query(Friends).filter(Friends.receiver_id == user.id,
                                                 not Friends.confirmed).all()
        data = {}
        for i, contact in enumerate(contacts):
            data[i] = {
                "id": contacts.id,
                "sender_id": contacts.sender_id,
                "receiver_id": contacts.receiver_id,
                "confirmed": contacts.confirmed,
            }
        return jsonify({'success': True, 'data': data})


@app.route("/contacts/add/<int:id>", methods=['POST'])
@jwt_required()
def add_contact(id):
    db_sess = db_session.create_session()
    current_user = get_jwt_identity()
    data = request.json.get('data')
    username = data.get('username')
    user = db_sess.query(User).filter(User.id == current_user).first()
    if not user:
        return jsonify({'error': "User not found"}), 404
    contact = db_sess.query(User).filter(User.id == id).first()
    if db_sess.query(Friends).filter(contact.id == sender_id).first()
    if task:
        db_sess.delete(task)
        db_sess.commit()
    else:
        abort(404)
    return jsonify({'success': True})
"""

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
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    db_sess = db_session.create_session()
    user1 = db_sess.query(User).filter(User.email == email).first()
    user2 = db_sess.query(User).filter(User.username == username).first()
    if user1 and user1.check_password(password):
        access_token = create_access_token(identity=user1.id)
        return jsonify({'success': True, "access_token": access_token, "login": user1.username}), 200
    elif user2 and user2.check_password(password):
        access_token = create_access_token(identity=user2.id)
        return jsonify({'success': True, "access_token": access_token, "login": user2.username}), 200
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
        return jsonify({'success': True, 'data': user_dict})
    return jsonify({'success': False, 'data': 'User not found'})


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
            return jsonify({'success': True, 'data': user_dict})
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
                return {'success': False, 'error': 'user_exists'}
            if db_sess.query(User).filter(User.email == user.email).first():
                return {'success': False, 'error': 'email_exists'}
            user.set_password(password)

            db_sess.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'User not found'})
    return jsonify({'success': True})


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
