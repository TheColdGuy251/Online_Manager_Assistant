import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Calendar(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'calendar'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    host_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("tasks.host_id"))
    task_name = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("tasks.id"))
    begin_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    end_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    is_private = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("tasks.is_private"))

    def __repr__(self):
        return f'<Calendar> {self.id} {self.task_name} {self.host_id} {self.begin_date} {self.end_date} {self.is_private}'