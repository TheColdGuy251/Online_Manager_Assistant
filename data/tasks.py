import datetime
import sqlalchemy
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class Task(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'tasks'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    task_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    begin_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    end_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    condition = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    priority = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    complete_perc = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    remind = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    date_remind = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    host_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    description = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    participants = relationship("TaskParticip", back_populates="task")
    is_in_calendar = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    calendaric = relationship("Calendar", back_populates="calendar_task", foreign_keys="[Calendar.task_id]")

    def __repr__(self):
        return f'<Task> {self.id} {self.task_name} {self.host_id} {self.begin_date} {self.end_date} {self.is_private} {self.description} {self.created_date} {self.date_remind} {self.remind} {self.condition} {self.priority}'

    def formatted_dates(self):
        formatted_begin_date = self.begin_date.strftime('%Y-%m-%d') if self.begin_date else None
        formatted_end_date = self.end_date.strftime('%Y-%m-%d') if self.end_date else None
        formatted_date_remind = self.date_remind.strftime('%Y-%m-%d') if self.date_remind else None
        return formatted_begin_date, formatted_end_date, formatted_date_remind