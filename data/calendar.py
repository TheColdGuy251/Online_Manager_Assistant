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
    task_name = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("tasks.task_name"))
    task_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("tasks.id"))
    cell_date = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    def __repr__(self):
        return f'<Calendar> {self.id} {self.task_name} {self.host_id} {self.cell_date}'

    def formatted_dates(self):
        formatted_cell_date = self.cell_date.strftime('%Y-%m-%d') if self.cell_date else None
        return formatted_cell_date
