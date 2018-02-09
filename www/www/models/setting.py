from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .meta import Base


class Setting(Base):
    __tablename__ = 'setting'

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime(timezone=True), nullable=False)
    created_by = Column(Text, ForeignKey('profile.username'), nullable=False)
    modified_on = Column(DateTime(timezone=True), nullable=False)
    modified_by = Column(Text, ForeignKey('profile.username'), nullable=False)
    key = Column(Text, nullable=False, unique=True)
    value = Column(Text, nullable=False)
    created_by_user = relationship('Profile', foreign_keys=[created_by])
    modified_by_user = relationship('Profile', foreign_keys=[modified_by])

    def __repr__(self):
        return '<Setting: {} - {}>'.format(self.key, self.value)
