from flask import Flask, render_template, redirect, request, make_response, session, abort, jsonify, url_for, \
    send_from_directory
from data import db_session
from data.users import User
from data.tasks import Task
from forms.register_form import RegisterForm
from forms.login_form import LoginForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import text
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tyuiu_secret_key'
CORS(app)
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/users.db")
    app.run()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/", methods=['GET', 'POST'])
def index():
    db_sess = db_session.create_session()
    return jsonify({'success': "OK"})




# регистрация аккаунта
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    db_sess = db_session.create_session()
    data = request.json.get('data')
    username = data.get('username')
    surname = data.get('surname')
    name = data.form.get('name')
    patronymic = data.get('patronymic')
    about = data.get('about')
    email = data.get('email')
    password = data.get('password')
    username = str(username).lower().strip()
    if db_sess.query(User).filter(User.username == username).first():
        return {'success': 'user_exists'}
    if db_sess.query(User).filter(User.email == email).first():
        return {'success': 'email_exists'}
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
    return jsonify({'success': "OK"})


# вход в аккаунт
@app.route('/login', methods=['GET', 'POST'])
def login():
    data = request.json.get('data')
    auth = data.get('auth')
    password = data.get('password')
    db_sess = db_session.create_session()
    if "@" in str(auth):
        user = db_sess.query(User).filter(User.email == auth).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            return jsonify({'success': "OK"})
        return jsonify({'success': "WrongAuth"})
    else:
        user = db_sess.query(User).filter(User.username == auth).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            return jsonify({'success': "OK"})
        return jsonify({'success': "WrongAuth"})


# выход из аккаунта
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# переход в профиль
@app.route("/profile/<string:username>", methods=['GET'])
def profile(username):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(username=username).first()

    if user:
        user_dict = {'username': user.username, 'surname': user.surname.decode('utf-8'), 'name': user.name.encode('utf-8'), 'patronymic': user.patronymic.decode('utf-8'), 'about': user.about.decode('utf-8'), 'created_date': user.created_date}
        return jsonify({'data': user_dict})
    return jsonify({'data': 'User not found'})


# изменение информации в профиле
@app.route("/profile/<string:username>/edit", methods=['GET', 'POST'])
def profile_edit(username):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(username=username).first()
    return render_template("user_profile.html", user=user)


@app.route('/test/Ilya', methods=['GET'])
def test():
    response = jsonify({'success': 'OK'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers',
                         'Authorization, Origin, X-Requested-With, Accept, X-PINGOTHER, Content-Type')

    return response

@app.route('/task/add', methods=['GET', 'POST'])
def add_task():
    db_sess = db_session.create_session()
    data = request.json.get('data')
    task_name = data.get('task_name')
    host_id = current_user
    begin_date = data.get('begin_date')
    end_date = data.get('end_date')
    is_private = data.get('is_private')
    priority = data.get('priority')
    description = data.get('description')
    created_date = data.get('created_date')
    task = Task(
        task_name=task_name,
        host_id=host_id,
        begin_date=begin_date,
        end_date=end_date,
        is_private=is_private,
        priority=priority,
        description=description,
        created_date=created_date
    )
    db_sess.add(task)
    db_sess.commit()
    return jsonify({'success': "OK"})
if __name__ == '__main__':
    main()
