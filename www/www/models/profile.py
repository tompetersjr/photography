import psycopg2

from sqlalchemy import Column, Text, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.hybrid import hybrid_property

from .meta import Base


class ProfileGroup(Base):
    __tablename__ = 'profile_group'

    rolename = Column(Text, primary_key=True, nullable=False, unique=True)
    created_on = Column(DateTime(timezone=True), nullable=False)
    created_by = Column(Text, ForeignKey('profile.username'), nullable=False)
    modified_on = Column(DateTime(timezone=True), nullable=False)
    modified_by = Column(Text, ForeignKey('profile.username'), nullable=False)
    title = Column(Text, nullable=False, unique=True)
    roles = Column(ARRAY(Text))

    def __repr__(self):
        return '<ProfileGroup: {}>'.format(self.rolename)

    @classmethod
    def get_all(cls, session):
        return session.query(ProfileGroup).order_by(ProfileGroup.rolename).all()

    @classmethod
    def create_role(cls, session, rolename):
        sql = text('SELECT 1 '
                   'FROM pg_roles '
                   'WHERE rolname=:rolename')
        result = session.execute(sql, {'rolename':rolename})

        if result.rowcount == 0:
            sql = "CREATE ROLE {}".format(rolename)
            session.execute(sql)

        return


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

    def __repr__(self):
        return '<Profile: {}>'.format(self.username)

    @hybrid_property
    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    @classmethod
    def get_all(cls, session):
        return session.query(Profile).order_by(Profile.first_name,
                                               Profile.last_name).all()

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

    @classmethod
    def authorize(cls, username, password):
        try:
            # Use psycopg2 to validate our login
            conn = psycopg2.connect(dbname='photos',
                                    user=username,
                                    password=password,
                                    host='postgres',
                                    port=5432)

            cur = conn.cursor()
            cur.execute('SELECT * FROM profile WHERE username=%s', (username,))
            profile = cur.fetchone()
            return profile[0]
        except psycopg2.OperationalError as e:
            return None
