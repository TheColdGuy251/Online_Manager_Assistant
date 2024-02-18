import flask
from . import db_session
from .users import User
from flask import jsonify, request

blueprint = flask.Blueprint(
    'user_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/user', methods=['GET'])
def get_users():
    db_sess = db_session.create_session()
    user = db_sess.query(User).all()
    return jsonify(
        {
            'user':
                [item.to_dict(only=('id', 'surname', 'name', 'patronymic', 'about', 'email', 'hashed_password', 'created_date'))
                 for item in user]
        }
    )


@blueprint.route('/api/user', methods=['POST'])
def create_user():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['id', 'surname', 'name', 'patronymic', 'about', 'email', 'hashed_password', 'created_date']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    user = User(
        id=request.json['id'],
        surname=request.json['surname'],
        name=request.json['name'],
        patronymic=request.json['patronymic'],
        about=request.json['about'],
        email=request.json['email'],
        hashed_password=request.json['hashed_password'],
        created_date=request.json['created_date']
    )
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:users_id>', methods=['DELETE'])
def delete_news(users_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(users_id)
    if not user:
        return jsonify({'error': 'Not found'})
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})