from flask import Flask, render_template, redirect, request, make_response, session, abort, jsonify, url_for, \
    send_from_directory
from data import db_session
from data.users import User
from forms.register_form import RegisterForm
from forms.login_form import LoginForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import text

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tyuiu_secret_key'

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


@app.route("/")
def index():
    db_sess = db_session.create_session()
    return render_template("index.html")


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
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


# выход из аккаунта
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# переход в профиль
@app.route("/profile/<string:username>", methods=['GET', 'POST'])
def profile(username):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(username=username).first()
    return "user"


# изменение профиля
@app.route("/profile/<string:username>/edit", methods=['GET', 'POST'])
@login_required
def profile_edit(username):
    if request.method == "POST":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == username).first()
        data = request.json.get('data')
        if user:
            data.get.username = user.username
            data.get.surname = user.surname
            data.form.get.name = user.name
            data.get.patronymic = user.patronymic
            data.get.about = user.about
            data.get.email = user.email
            data.get.password = user.password
        else:
            abort(404)
    if request.method == "POST":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == username).first()
        if user:
            user.username = data.get.username
            user.surname = data.get.surname
            user.name = data.form.get.name
            user.patronymic = data.get.patronymic
            user.about = data.get.about
            user.email = data.get.email
            user.password = data.get.password
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return jsonify({'success': "OK"})


# информация о пользователе
@app.route("/profile/<string:username>/info", methods=['GET', 'POST'])
def profile_info(username):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(username=username).first()
    return jsonify({'Username': user.username, 'Surname': user.surname, 'Name': user.name, 'Patrinymic': user.patronymic, 'Email': user.email})


# удаление профиля
@app.route("/profile/<string:username>/delete", methods=['GET', 'POST'])
@login_required
def news_delete(username):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(username=username).first()
    if user:
        db_sess.delete(user)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/test/Vlada', methods=['GET'])
def test():
    response = jsonify({'luck': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers',
                         'Authorization, Origin, X-Requested-With, Accept, X-PINGOTHER, Content-Type')

    return response


if __name__ == '__main__':
    main()