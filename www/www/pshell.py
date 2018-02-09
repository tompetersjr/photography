import transaction

from www.models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )


def setup(env):
    settings = env['registry'].settings
    engine = get_engine(settings)
    session_factory = get_session_factory(engine)
    env['dbsession'] = get_tm_session(session_factory, transaction.manager)