import bcrypt
import datetime
import os
import slugify
import sys
import transaction

from alembic.config import Config
from alembic import command

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars
from sqlalchemy import text

from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )

from ..models.album import Album
from ..models.contact import Contact
from ..models.navigation import Navigation
from ..models.photo import Photo, PhotoAlbum
from ..models.setting import Setting
from ..models.tasks import Task
from ..models.profile import Profile


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    #Base.metadata.create_all(engine)

    #alembic_cfg = Config(config_uri)
    #command.stamp(alembic_cfg, "head")

    session_factory = get_session_factory(engine)
    
    profile_id = 'photo'
    password = 'password'

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        username = 'jdoe'
        profile = Profile(created_on=datetime.datetime.now(), created_by=profile_id,
                          modified_on=datetime.datetime.now(), modified_by=profile_id,
                          username=username,
                          first_name='John', last_name='Doe',
                          email='jdoe@thisistheemailaddress.com',
                          active=True)
        profile.create_role(dbsession, username, password)
        dbsession.add(profile)

        username = 'dpowers'
        profile = Profile(created_on=datetime.datetime.now(), created_by=profile_id,
                          modified_on=datetime.datetime.now(), modified_by=profile_id,
                          username=username,
                          first_name='Dan', last_name='Powers',
                          email='dpowers@thisistheemailaddress.com',
                          active=True)
        profile.create_role(dbsession, username, password)
        dbsession.add(profile)

        username = 'gsmith'
        profile = Profile(created_on=datetime.datetime.now(), created_by=profile_id,
                          modified_on=datetime.datetime.now(), modified_by=profile_id,
                          username=username,
                          first_name='Gary', last_name='Smith',
                          email='gsmith@thisistheemailaddress.com',
                          active=True)
        profile.create_role(dbsession, username, password)
        dbsession.add(profile)

        username = 'rwinter'
        profile = Profile(created_on=datetime.datetime.now(), created_by=profile_id,
                          modified_on=datetime.datetime.now(), modified_by=profile_id,
                          username=username,
                          first_name='Ray', last_name='Winter',
                          email='rwinter@thisistheemailaddress.com',
                          active=True)
        profile.create_role(dbsession, username, password)
        dbsession.add(profile)

        username = 'gsanders'
        profile = Profile(created_on=datetime.datetime.now(), created_by=profile_id,
                          modified_on=datetime.datetime.now(), modified_by=profile_id,
                          username=username,
                          first_name='Greg', last_name='Sanders',
                          email='gsanders@thisistheemailaddress.com',
                          active=True)
        profile.create_role(dbsession, username, password)
        dbsession.add(profile)

        nav = Setting(created_on=datetime.datetime.now(), created_by=profile_id,
                      modified_on=datetime.datetime.now(), modified_by=profile_id,
                      key='site_name',
                      value='My Photography')
        dbsession.add(nav)
        nav = Setting(created_on=datetime.datetime.now(), created_by=profile_id,
                      modified_on=datetime.datetime.now(), modified_by=profile_id,
                      key='site_photographer',
                      value='John Doe')
        dbsession.add(nav)
        nav = Setting(created_on=datetime.datetime.now(), created_by=profile_id,
                      modified_on=datetime.datetime.now(), modified_by=profile_id,
                      key='site_contact',
                      value='info@myphotoemailaddressishere.com')
        dbsession.add(nav)

        dbsession.execute('ALTER ROLE administrators WITH USER jdoe')
        dbsession.execute('CREATE ROLE family WITH USER gsanders, rwinter')
        dbsession.execute('CREATE ROLE friends WITH USER dpowers, gsmith')
        dbsession.execute('CREATE ROLE client WITH USER rwinter')

        dbsession.execute('GRANT SELECT, INSERT, UPDATE, DELETE ON album TO family, friends, client')
        dbsession.execute('GRANT SELECT, INSERT, UPDATE, DELETE ON contact TO family, friends, client')
        dbsession.execute('GRANT SELECT, INSERT, UPDATE, DELETE ON navigation TO family, friends, client')
        dbsession.execute('GRANT SELECT, INSERT, UPDATE, DELETE ON photo TO family, friends, client')
        dbsession.execute('GRANT SELECT, INSERT, UPDATE, DELETE ON setting TO family, friends, client')
        dbsession.execute('GRANT SELECT, INSERT, UPDATE, DELETE ON task TO family, friends, client')
        dbsession.execute('GRANT SELECT, INSERT, UPDATE, DELETE ON profile TO family, friends, client')
        dbsession.execute('GRANT SELECT, INSERT, UPDATE, DELETE ON photo_album TO family, friends, client')

        dbsession.execute('GRANT family, friends, client, authenticated, unauthenticated TO administrators')
        dbsession.execute('GRANT authenticated, unauthenticated TO family')
        dbsession.execute('GRANT authenticated, unauthenticated TO friends')
        dbsession.execute('GRANT authenticated, unauthenticated TO client')
