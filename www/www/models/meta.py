import datetime

from sqlalchemy import inspect
from sqlalchemy.event import listens_for
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData

# Recommended naming convention used by Alembic, as various different database
# providers will autogenerate vastly different names making migrations more
# difficult. See: http://alembic.zzzcomputing.com/en/latest/naming.html
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


class BaseModel(object):
    @classmethod
    def find_one(cls, session, id):
        return session.query(cls).filter(cls.get_id() == id).one()

    @classmethod
    def find_update(cls, session, id, args):
        return session.query(cls).filter(
            cls.get_id() == id).update(
            args, synchronize_session=False)

    @classmethod
    def get_id(cls):
        pass

    def to_dict(self):
        cols = set(self.__table__.columns.keys())
        fields = set(self.FIELDS)
        intersection = cols.intersection(fields)
        return dict(map(
            lambda key:
                (key,
                    (lambda value: self.FIELDS[key](value) if value else None)
                    (getattr(self, key))),
                intersection))


@listens_for(BaseModel, 'before_insert', propagate=True)
def receive_before_insert(mapper, connection, target):
    if 'username' in inspect(target).session.info:
        username = inspect(target).session.info['username']

        if hasattr(target, 'created_by'):
            if target.created_by is None:
                target.created_by = username
        if hasattr(target, 'modified_by'):
            if target.modified_by is None:
                target.modified_by = username

    # Make sure the created on and created by exist
    # before we go updating them.
    if hasattr(target, 'created_on'):
        target.created_on = datetime.datetime.utcnow()
    if hasattr(target, 'modified_on'):
        target.modified_on = datetime.datetime.utcnow()
    return


@listens_for(BaseModel, 'before_update', propagate=True)
def receive_before_update(mapper, connection, target):
    if 'username' in inspect(target).session.info:
        username = inspect(target).session.info['username']

        if hasattr(target, 'modified_by'):
            target.modified_by = username

    if hasattr(target, 'modified_on'):
        target.modified_on = datetime.datetime.utcnow()
    return


metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(cls=BaseModel, metadata=metadata)