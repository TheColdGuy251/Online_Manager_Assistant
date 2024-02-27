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
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Такой пользователь уже есть")
        if " " in form.name.data:
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
@app.route("/profile/<int:id>", methods=['GET', 'POST'])
def profile(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(id=id).first()
    return render_template("user_profile.html", user=user)


# изменение информации в профиле
@app.route("/profile/<int:id>/edit", methods=['GET', 'POST'])
def profile_edit(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(id=id).first()
    return render_template("user_profile.html", user=user)


@app.route('/test', methods=['GET'])
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