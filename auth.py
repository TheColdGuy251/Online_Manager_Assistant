from flask import request, jsonify, Blueprint
from data import db_session
from data.users import User
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, unset_jwt_cookies


auth_blueprint = Blueprint(
    'auth',
    __name__,
)


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


@auth_blueprint.route('/register', methods=['GET', 'POST'])
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
        db_sess.close()
        return jsonify({'success': True, 'access_token': access_token})


# вход в аккаунт
@auth_blueprint.route('/login', methods=['GET', 'POST'])
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
    db_sess.close()
    return jsonify({'success': False, "Error": "WrongAuth"})


@auth_blueprint.route("/logout", methods=["POST"])
def logout():
    unset_jwt_cookies(jsonify({"Success": True}))
    return jsonify({"Success": True})


# переход в профиль
@auth_blueprint.route("/profile", methods=['GET'])
def profile():
    current_user_id = get_jwt_identity()
    db_sess = db_session.create_session()
    current_user = get_current_user(db_sess, current_user_id)
    if not current_user:
        return jsonify({'error': "User not found"}), 404
    data = {
        "id": current_user.id,
        "username": current_user.username,
        "surname": current_user.surname,
        "name": current_user.name,
        "patronymic": current_user.patronymic,
        "about": current_user.about,
        "email": current_user.email,
        "position": current_user.position,
        "created_date": current_user.created_date,
    }
    db_sess.close()
    return jsonify({'success': True, 'data': data})


# изменение профиля
@auth_blueprint.route("/profile/edit", methods=['GET', 'POST'])
@jwt_required()
def profile_edit(username):
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == username).first()
        if user:
            user_dict = {'username': user.username, 'surname': user.surname, 'name': user.name,
                         'patronymic': user.patronymic, 'about': user.about, 'email': user.email,
                         'created_date': user.created_date}
            db_sess.close()
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
            db_sess.close()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'User not found'})
    return jsonify({'success': True})


# удаление профиля
@auth_blueprint.route("/profile/delete", methods=['GET', 'POST'])
@jwt_required()
def profile_delete():
    current_user_id = get_jwt_identity()
    db_sess = db_session.create_session()
    current_user = get_current_user(db_sess, current_user_id)
    if not current_user:
        return jsonify({'error': "User not found"}), 404
    if current_user:
        db_sess.delete(current_user)
        db_sess.commit()
    else:
        return jsonify({'success': False, 'Error': 'User not found'})
    return jsonify({'success': True})