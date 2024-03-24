import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Task(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'tasks'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    task_name = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    begin_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    end_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    condition = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    priority = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    complete_perc = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    remind = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    date_remind = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    host_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    description = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f'<Task> {self.id} {self.task_name} {self.host_id} {self.begin_date} {self.end_date} {self.is_private} {self.description} {self.created_date} {self.date_remind} {self.remind} {self.condition} {self.priority}'