from flask import Flask, make_response, jsonify
from data import db_session
from datetime import datetime, timedelta, timezone
from data.users import User
from contacts import contact_blueprint
from tasks import tasks_blueprint
from auth import auth_blueprint
from calendar_api import calendar_blueprint
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, get_jwt,\
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
app.register_blueprint(calendar_blueprint)


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

if __name__ == '__main__':
    main()