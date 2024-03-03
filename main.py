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
import json

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


@app.route("/")
def index():
    db_sess = db_session.create_session()
    return render_template("index.html")


# регистрация аккаунта
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    '''
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
    '''

    form = RegisterForm()
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
    '''
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
    '''

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
    if user:
        user_dict = {'username': user.username,
                     'surname': user.surname,
                     'name': user.name,
                     'patronymic': user.patronymic,
                     'about': user.about,
                     'email': user.email,
                     'created_date': user.created_date}
        return jsonify({'data': user_dict})
    return jsonify({'data': 'User not found'})
    '''
    user = str(users)[7:].replace(" ", " | ")
    str1 = "Id, Username, Surname, Name, Patronymic, Email"
    keys = str1.split(", ")
    values = user. split(" | ")
    dictionary = dict(zip(keys, values))
    return dictionary

    dict_utf = {
        'u0410': 'А', 'u0430': 'а',
        'u0411': 'Б', 'u0431': 'б',
        'u0412': 'В', 'u0432': 'в',
        'u0413': 'Г', 'u0433': 'г',
        'u0414': 'Д', 'u0434': 'д',
        'u0415': 'Е', 'u0435': 'е',
        'u0401': 'Ё', 'u0451': 'ё',
        'u0416': 'Ж', 'u0436': 'ж',
        'u0417': 'З', 'u0437': 'з',
        'u0418': 'И', 'u0438': 'и',
        'u0419': 'Й', 'u0439': 'й',
        'u041a': 'К', 'u043a': 'к',
        'u041b': 'Л', 'u043b': 'л',
        'u041c': 'М', 'u043c': 'м',
        'u041d': 'Н', 'u043d': 'н',
        'u041e': 'О', 'u043e': 'о',
        'u041f': 'П', 'u043f': 'п',
        'u0420': 'Р', 'u0440': 'р',
        'u0421': 'С', 'u0441': 'с',
        'u0422': 'Т', 'u0442': 'т',
        'u0423': 'У', 'u0443': 'у',
        'u0424': 'Ф', 'u0444': 'ф',
        'u0425': 'Х', 'u0445': 'х',
        'u0426': 'Ц', 'u0446': 'ц',
        'u0427': 'Ч', 'u0447': 'ч',
        'u0428': 'Ш', 'u0448': 'ш',
        'u0429': 'Щ', 'u0449': 'щ',
        'u042a': 'Ъ', 'u044a': 'ъ',
        'u042d': 'Ы', 'u044b': 'ы',
        'u042c': 'Ь', 'u044c': 'ь',
        'u042d': 'Э', 'u044d': 'э',
        'u042e': 'Ю', 'u044e': 'ю',
        'u042f': 'Я', 'u044f': 'я',
    }

    s_surname = user.surname
    repr(s_surname)
    data_surname = json.dumps(s_surname)
    json.dumps(s_surname, ensure_ascii=False)
    p_text_surname = json.loads(data_surname)
    surname = p_text_surname
    #return surname

    s_name = user.name
    repr(s_name)
    data_name = json.dumps(s_name)
    json.dumps(s_name, ensure_ascii=False)
    name = json.loads(data_name)
    #return name

    s_patronymic = user.patronymic
    repr(s_patronymic)
    data_patronymic = json.dumps(s_patronymic)
    json.dumps(s_patronymic, ensure_ascii=False)
    patronymic = json.loads(data_patronymic)
    #return patronymic

    s_about = user.about
    repr(s_about)
    data_about = json.dumps(s_about)
    json.dumps(s_about, ensure_ascii=False)
    about = json.loads(data_about)
    #return about
    '''

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

# добавление задач
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

# редактирование задач
@app.route("/tasks/<int: id>/edit", methods=['GET', 'POST'])
@login_required
def profile_edit(id):
    if request.method == "GET":
        db_sess = db_session.create_session()
        task = db_sess.query(Task).filter(Task.id == id).first()
        if task:
            task_dict = {'name' : task.name,
                         'host_id': task.host_id,
                         'begin_date': task.begin_date,
                         'end_date': task.end_date,
                         'is_private': task.is_private,
                         'priority': task.priority,
                         'description': task.description,
                         'created_date': task.created_date}
            return jsonify({'data': task_dict})
        else:
            jsonify({'data': 'Task not found'})
    if request.method == "POST":
        db_sess = db_session.create_session()
        task = db_sess.query(Task).filter(Task.id == id).first()
        if task:
            data = request.json.get('data')
            task.name = data.get('task_name')
            task.host_id = current_user
            task.begin_date = data.get('begin_date')
            task.end_date = data.get('end_date')
            task.is_private = data.get('is_private')
            task.priority = data.get('priority')
            task.description = data.get('description')
            task.created_date = data.get('created_date')

            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return jsonify({'success': "OK"})

# удаление задач
@app.route("/tasks/<int:id>/delete", methods=['GET', 'POST'])
def news_delete(id):
    db_sess = db_session.create_session()
    task = db_sess.query(Task).filter_by(id = id).first()
    if task:
        db_sess.delete(task)
        db_sess.commit()
    else:
        abort(404)
    return jsonify({'success': 'OK'})

@app.route('/test/Roman', methods=['GET'])
def test():
    response = jsonify({'success': 'OK'})
    return response

if __name__ == '__main__':
    main()