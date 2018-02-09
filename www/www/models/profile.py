from sqlalchemy import Column, Boolean, Text, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.event import listens_for
from sqlalchemy.ext.hybrid import hybrid_property

from .meta import Base


class Profile(Base):
    __tablename__ = 'profile'

    username = Column(Text, primary_key=True, nullable=False, unique=True)
    created_on = Column(DateTime(timezone=True), nullable=False)
    created_by = Column(Text, ForeignKey('profile.username'), nullable=False)
    modified_on = Column(DateTime(timezone=True), nullable=False)
    modified_by = Column(Text, ForeignKey('profile.username'), nullable=False)
    roles = Column(ARRAY(Text))
    first_name = Column(Text)
    last_name = Column(Text)
    email = Column(Text)
    active = Column(Boolean, nullable=False)

    def __repr__(self):
        return '<Profile: {}>'.format(self.username)

    @hybrid_property
    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    @classmethod
    def create_role(cls, session, username, password):
        sql = text('SELECT 1 '
                   'FROM pg_roles '
                   'WHERE rolname=:username')
        result = session.execute(sql, {'username':username})

        if result.rowcount == 0:
            sql = "CREATE ROLE {} WITH LOGIN password '{}'".format(username,
                                                                   password)
            session.execute(sql)

        return
