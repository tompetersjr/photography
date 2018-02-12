import zope.sqlalchemy
from pyramid.threadlocal import get_current_request
from sqlalchemy import engine_from_config
from sqlalchemy.event import listens_for
from sqlalchemy.orm import configure_mappers
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

# import or define all models here to ensure they are attached to the
# Base.metadata prior to any initialization routines
from .album import Album
from .contact import Contact
from .navigation import Navigation
from .photo import Photo, PhotoAlbum, PhotoTag, PhotoFile, PhotoSize, Tag
from .profile import Profile, ProfileGroup
from .setting import Setting
from .tasks import Task

# run configure_mappers after defining all of the models to ensure
# all relationships can be setup
configure_mappers()


def get_engine(settings, prefix='sqlalchemy.'):
    return engine_from_config(settings, prefix)


def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def get_tm_session(session_factory, transaction_manager):
    """
    Get a ``sqlalchemy.orm.Session`` instance backed by a transaction.

    This function will hook the session to the transaction manager which
    will take care of committing any changes.

    - When using pyramid_tm it will automatically be committed or aborted
      depending on whether an exception is raised.

    - When using scripts you should wrap the session in a manager yourself.
      For example::

          import transaction

          engine = get_engine(settings)
          session_factory = get_session_factory(engine)
          with transaction.manager:
              dbsession = get_tm_session(session_factory, transaction.manager)

    """
    dbsession = session_factory()
    zope.sqlalchemy.register(
        dbsession, transaction_manager=transaction_manager)
    return dbsession


def includeme(config):
    """
    Initialize the model for a Pyramid app.

    Activate this setup using ``config.include('www.models')``.

    """
    settings = config.get_settings()
    settings['tm.manager_hook'] = 'pyramid_tm.explicit_manager'

    # use pyramid_tm to hook the transaction lifecycle to the request
    config.include('pyramid_tm')

    # use pyramid_retry to retry a request when transient exceptions occur
    config.include('pyramid_retry')

    session_factory = get_session_factory(get_engine(settings))
    config.registry['dbsession_factory'] = session_factory

    # make request.dbsession available for use in Pyramid
    config.add_request_method(
        # r.tm is the transaction manager used by pyramid_tm
        lambda r: get_tm_session(session_factory, r.tm),
        'dbsession',
        reify=True
    )

    @listens_for(session_factory, 'after_begin')
    def switch_to_user(session, sqla_txn, connection):
        set_local_role = text("SET LOCAL ROLE :role_name;")
        request = get_current_request()
        if request.authenticated_userid:
            connection.execute(set_local_role, role_name=request.user.username)
        else:
            connection.execute(set_local_role, role_name='anonymous')
