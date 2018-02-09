from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.dialects.postgresql import ARRAY

from .meta import Base


class Contact(Base):
    __tablename__ = 'contact'

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime(timezone=True), nullable=False)
    roles = Column(ARRAY(Text))
    to_email = Column(Text, nullable=False)
    from_name = Column(Text, nullable=False)
    from_email = Column(Text, nullable=False)
    subject = Column(Text, nullable=False)
    message = Column(Text, nullable=False)

    def __repr__(self):
        return '<Contact: {} ({}) - {}>'.format(self.from_name, self.from_email, self.subject)
