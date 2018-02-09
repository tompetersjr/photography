from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from .meta import Base


class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime(timezone=True), nullable=False)
    created_by = Column(Text, ForeignKey('profile.username'), nullable=False)
    roles = Column(ARRAY(Text))
    title = Column(Text, nullable=False)
    status = Column(Integer, nullable=False)
    created_by_user = relationship('Profile', foreign_keys=[created_by])

    def __repr__(self):
        return '<Task: {}>'.format(self.title)
