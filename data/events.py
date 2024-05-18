import datetime
import sqlalchemy
from sqlalchemy.orm import relationship
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Events(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'events'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    host_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("tasks.host_id"))
    event_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    event_descr = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    cell_date = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    participants = relationship("EventParticip", back_populates="event")

    def __repr__(self):
        return f'<Events> {self.id} {self.event_name} {self.host_id} {self.cell_date} {self.event_descr}'

    def formatted_dates(self):
        formatted_cell_date = self.cell_date.strftime('%Y-%m-%d') if self.cell_date else None
        return formatted_cell_date
