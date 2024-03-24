import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class TaskChat(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'task_chat'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    task_participants = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("task_participants.id"))
    sender_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    message = sqlalchemy.Column(sqlalchemy.Text)

    def __repr__(self):
        return f'<TaskChat> {self.id} {self.task_participants} {self.sender_id} {self.message}'