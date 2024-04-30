from flask import request, jsonify, Blueprint
from data import db_session
from data.users import User
from data.friends import Friends
from sqlalchemy import or_, and_
from flask_jwt_extended import jwt_required, get_jwt_identity


contact_blueprint = Blueprint(
    'contacts',
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


@contact_blueprint.route("/contacts", methods=['GET'])
@jwt_required()
def load_contacts():
    current_user_id = get_jwt_identity()
    db_sess = db_session.create_session()

    current_user = get_current_user(db_sess, current_user_id)
    if not current_user:
        return jsonify({'error': "User not found"}), 404

    contacts = db_sess.query(Friends).filter(
        or_(Friends.sender_id == current_user_id, Friends.receiver_id == current_user_id),
        Friends.confirmed == 1
    ).all()

    data = [get_contact_details(db_sess, contact, current_user_id) for contact in contacts]
    return jsonify({'success': True, 'user': [d for d in data if d]})


@contact_blueprint.route("/contacts/delete", methods=['POST'])
@jwt_required()
def delete_contact():
    current_user_id = get_jwt_identity()
    data = request.json.get('data')
    other_user_id = data.get('id')

    db_sess = db_session.create_session()

    current_user = get_current_user(db_sess, current_user_id)
    if not current_user:
        return jsonify({'error': "User not found"}), 404

    contact = db_sess.query(Friends).filter(
        or_(
            and_(Friends.sender_id == current_user_id, Friends.receiver_id == other_user_id),
            and_(Friends.sender_id == other_user_id, Friends.receiver_id == current_user_id)
        ),
        Friends.confirmed == 1
    ).first()

    if contact:
        db_sess.delete(contact)
        db_sess.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'error': "Friend relationship not found"}), 404


@contact_blueprint.route("/contacts/find", methods=['GET'])
@jwt_required()
def load_users():
    current_user_id = get_jwt_identity()
    db_sess = db_session.create_session()

    users = db_sess.query(User).filter(User.id != current_user_id).all()

    data = []
    for user in users:
        contact = db_sess.query(Friends).filter(
            or_(
                and_(Friends.sender_id == current_user_id, Friends.receiver_id == user.id),
                and_(Friends.sender_id == user.id, Friends.receiver_id == current_user_id)
            )
        ).first()
        if not contact:
            data.append({
                "id": user.id,
                "username": user.username,
                "surname": user.surname,
                "name": user.name,
                "patronymic": user.patronymic,
                "email": user.email,
                "about": user.about,
            })

    return jsonify({'success': True, 'data': data})


@contact_blueprint.route("/contacts/requests", methods=['GET'])
@jwt_required()
def load_requests():
    current_user_id = get_jwt_identity()
    db_sess = db_session.create_session()

    current_user = get_current_user(db_sess, current_user_id)
    if not current_user:
        return jsonify({'error': "User not found"}), 404

    contacts = db_sess.query(Friends).filter(
        Friends.receiver_id == current_user_id,
        Friends.confirmed == 0
    ).all()

    data = [get_contact_details(db_sess, contact, current_user_id) for contact in contacts]
    return jsonify({'success': True, 'users': [d for d in data if d]})


@contact_blueprint.route("/contacts/requests/confirm", methods=['POST'])
@jwt_required()
def confirm_request():
    current_user_id = get_jwt_identity()
    data = request.json.get('data')
    other_user_id = data.get('id')
    status = bool(data.get('status'))

    db_sess = db_session.create_session()

    current_user = get_current_user(db_sess, current_user_id)
    if not current_user:
        return jsonify({'error': "User not found"}), 404

    contact = db_sess.query(Friends).filter(
        Friends.sender_id == other_user_id,
        Friends.receiver_id == current_user_id
    ).first()

    if contact:
        if status:
            contact.confirmed = status
        else:
            db_sess.delete(contact)
        db_sess.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'error': "Friend request not found"}), 404


@contact_blueprint.route("/contacts/add", methods=['POST'])
@jwt_required()
def add_contact():
    current_user_id = get_jwt_identity()
    data = request.json.get('data')
    other_user_ids = data.get('ids')
    db_sess = db_session.create_session()
    current_user = get_current_user(db_sess, current_user_id)
    if not current_user:
        return jsonify({'error': "User not found"}), 404
    for other_user_id in other_user_ids:
        existing_request = db_sess.query(Friends).filter(
            Friends.sender_id == current_user_id,
            Friends.receiver_id == other_user_id
        ).first()
        if existing_request:
            return jsonify({'error': "Friend request already sent"}), 400

        contact_new = Friends(
            sender_id=current_user_id,
            receiver_id=other_user_id,
            confirmed=False,
        )
        db_sess.add(contact_new)
        db_sess.commit()
    return jsonify({'success': True})