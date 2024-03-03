import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class PersChat(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'personal_chat'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    sender_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    message = sqlalchemy.Column(sqlalchemy.Text)

    def __repr__(self):
        return f'<PersChat> {self.id} {self.task_id} {self.user_id}'