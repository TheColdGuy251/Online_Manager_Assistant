import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class EventParticip(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'event_participants'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    event_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("events.id"))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    event = relationship("Events", back_populates="participants")

    def __repr__(self):
        return f'<EventParticip> {self.id} {self.event_id} {self.user_id}'