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
    form = RegisterForm()
    if request.method == "POST" and not form.validate_on_submit():
        db_sess = db_session.create_session()
        data = request.json.get('data')
        username = data.get('username')
        surname = data.get('surname')
        name = data.form.get('name')
        patronymic = data.get('patronymic')
        about = data.get('about')
        email = data.get('email')
        password = data.get('password')
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
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        form.username.data = str(form.username.data).lower().strip()
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Пароли не совпадают")

        if db_sess.query(User).filter(User.username == form.username.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Такое имя пользователя уже есть")
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Такой адрес электронной почты уже есть")
        if " " in form.username.data:
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Нельзя использовать пробел в имени")
        user = User(
            username=form.username.data,
            surname=form.surname.data,
            name=form.name.data,
            patronymic=form.patronymic.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


# вход в аккаунт
@app.route('/login', methods=['GET', 'POST'])
def login():
    data = request.json.get('data')
    auth = data.get('auth')
    password = data.get('password')
    remember = data.get('remember')
    db_sess = db_session.create_session()
    if "@" in str(auth):
        user = db_sess.query(User).filter(User.email == auth).first()
    else:
        user = db_sess.query(User).filter(User.username == auth).first()
    if user and user.check_password(password):
        if bool(remember):
            login_user(user, remember=True)
        else:
            login_user(user, remember=False)
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
        user_dict = {'username': user.username, 'surname': user.surname, 'name': user.name,
                     'patronymic': user.patronymic, 'about': user.about, 'email': user.email,
                     'created_date': user.created_date}
        return jsonify({'data': user_dict})
    return jsonify({'data': 'User not found'})


# изменение профиля
@app.route("/profile/<string:username>/edit", methods=['GET', 'POST'])
@login_required
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
            return redirect('/')
        else:
            abort(404)
    return jsonify({'success': "OK"})


@app.route('/test/Ilya', methods=['GET'])
def test():
    response = jsonify({'success': 'OK'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers',
                         'Authorization, Origin, X-Requested-With, Accept, X-PINGOTHER, Content-Type')

    return response


if __name__ == '__main__':
    main()