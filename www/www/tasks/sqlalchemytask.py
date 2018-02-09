import celery
import transaction

from pyramid.paster import (
    get_appsettings,
)
from www.models import (
    get_engine,
    get_session_factory,
    get_tm_session,
)
from www.celeryconf import app


class SqlAlchemyTask(celery.Task):

    def __init__(self):
        self.dbsession = None

        settings = get_appsettings('development.ini')

        engine = get_engine(settings)
        session_factory = get_session_factory(engine)
        self.dbsession = get_tm_session(session_factory, transaction.manager)

