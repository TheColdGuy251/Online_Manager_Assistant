import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class TaskParticip(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'task_participants'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    task_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("tasks.id"))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    task = relationship("Task", back_populates="participants")

    def __repr__(self):
        return f'<TaskParticip> {self.id} {self.task_id} {self.user_id}'