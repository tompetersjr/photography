import bcrypt
import datetime
import os
import sys
import transaction
import slugify

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
from ..models.profile import Profile, ProfileGroup
from ..models.photo import Photo, PhotoAlbum, PhotoTag, \
    Tag, PhotoSize, PhotoFile
from ..models.setting import Setting
from ..models.tasks import Task


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
    Base.metadata.create_all(engine)

    #alembic_cfg = Config(config_uri)
    #command.stamp(alembic_cfg, "head")

    session_factory = get_session_factory(engine)

    profile_id = 'photo'

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        profile = Profile(username='photo',
                          created_on=datetime.datetime.now(),
                          created_by=profile_id,
                          modified_on=datetime.datetime.now(),
                          modified_by=profile_id,
                          first_name='Photo',
                          last_name='Application',
                          email='photo@thisistheemailaddress.com')
        dbsession.add(profile)

        group = ProfileGroup(rolename='administrators',
                             created_on=datetime.datetime.now(),
                             created_by=profile_id,
                             modified_on=datetime.datetime.now(),
                             modified_by=profile_id,
                             title='Administrators')
        dbsession.add(group)

        setting = Setting(created_on=datetime.datetime.now(),
                          created_by=profile_id,
                          modified_on=datetime.datetime.now(),
                          modified_by=profile_id,
                          key='storage_username',
                          value='')
        dbsession.add(setting)
        setting = Setting(created_on=datetime.datetime.now(),
                          created_by=profile_id,
                          modified_on=datetime.datetime.now(),
                          modified_by=profile_id,
                          key='storage_key',
                          value='')
        dbsession.add(setting)
        setting = Setting(created_on=datetime.datetime.now(),
                          created_by=profile_id,
                          modified_on=datetime.datetime.now(),
                          modified_by=profile_id,
                          key='storage_path',
                          value='/srv/uploads')
        dbsession.add(setting)

        nav = Navigation(id=1,
                         created_on=datetime.datetime.now(),
                         created_by=profile_id,
                         modified_on=datetime.datetime.now(),
                         modified_by=profile_id,
                         roles=['unauthenticated'],
                         menu_id='main',
                         sort_order=1,
                         page_title='Home',
                         route='home',)
        dbsession.add(nav)
        nav = Navigation(id=2,
                         created_on=datetime.datetime.now(),
                         created_by=profile_id,
                         modified_on=datetime.datetime.now(),
                         modified_by=profile_id,
                         roles=['unauthenticated'],
                         menu_id='main',
                         sort_order=2,
                         page_title='Landscapes',
                         route='landscapes',)
        dbsession.add(nav)
        nav = Navigation(id=3,
                         created_on=datetime.datetime.now(),
                         created_by=profile_id,
                         modified_on=datetime.datetime.now(),
                         modified_by=profile_id,
                         roles=['unauthenticated'],
                         menu_id='main',
                         sort_order=3,
                         page_title='Family',
                         route='family',)
        dbsession.add(nav)
        nav = Navigation(id=4,
                         created_on=datetime.datetime.now(),
                         created_by=profile_id,
                         modified_on=datetime.datetime.now(),
                         modified_by=profile_id,
                         roles=['authenticated'],
                         menu_id='main',
                         sort_order=4,
                         page_title='All Albums',
                         route='album',
                         params={
                            'album': 'root'
                         })
        dbsession.add(nav)
        nav = Navigation(id=5,
                         created_on=datetime.datetime.now(),
                         created_by=profile_id,
                         modified_on=datetime.datetime.now(),
                         modified_by=profile_id,
                         roles=['unauthenticated'],
                         menu_id='main',
                         sort_order=5,
                         page_title='About',
                         route='about',)
        dbsession.add(nav)
        nav = Navigation(id=6,
                         created_on=datetime.datetime.now(),
                         created_by=profile_id,
                         modified_on=datetime.datetime.now(),
                         modified_by=profile_id,
                         roles=['unauthenticated'],
                         menu_id='main',
                         sort_order=6,
                         page_title='Contact',
                         route='contact',)
        dbsession.add(nav)
        nav = Navigation(id=7,
                         created_on=datetime.datetime.now(),
                         created_by=profile_id,
                         modified_on=datetime.datetime.now(),
                         modified_by=profile_id,
                         roles=['administrators'],
                         menu_id='main',
                         sort_order=7,
                         page_title='Admin',
                         route='admin-dashboard',)
        dbsession.add(nav)
        nav = Navigation(id=8,
                         created_on=datetime.datetime.now(),
                         created_by=profile_id,
                         modified_on=datetime.datetime.now(),
                         modified_by=profile_id,
                         roles=['administrators'],
                         menu_id='admin',
                         sort_order=7,
                         page_title='Dashboard',
                         route='admin-dashboard',)
        dbsession.add(nav)
        nav = Navigation(id=9,
                         created_on=datetime.datetime.now(),
                         created_by=profile_id,
                         modified_on=datetime.datetime.now(),
                         modified_by=profile_id,
                         roles=['administrators'],
                         menu_id='admin',
                         sort_order=7,
                         page_title='Users',
                         route='admin-users',)
        dbsession.add(nav)
        nav = Navigation(id=10,
                         created_on=datetime.datetime.now(),
                         created_by=profile_id,
                         modified_on=datetime.datetime.now(),
                         modified_by=profile_id,
                         roles=['administrators'],
                         menu_id='admin',
                         sort_order=7,
                         page_title='Roles',
                         route='admin-roles',)
        dbsession.add(nav)

        size = PhotoSize(id=1,
                         created_on=datetime.datetime.now(),
                         created_by=profile_id,
                         modified_on=datetime.datetime.now(),
                         modified_by=profile_id,
                         roles=['administrators'],
                         title='Original',
                         slug='original',
                         is_system=True,
                         is_active=True)
        dbsession.add(size)
        size = PhotoSize(id=2,
                         created_on=datetime.datetime.now(),
                         created_by=profile_id,
                         modified_on=datetime.datetime.now(),
                         modified_by=profile_id,
                         roles=['administrators'],
                         title='Square',
                         slug='square',
                         is_system=False,
                         is_active=True,
                         width=120,
                         height=120)
        dbsession.add(size)
        size = PhotoSize(id=3,
                         created_on=datetime.datetime.now(),
                         created_by=profile_id,
                         modified_on=datetime.datetime.now(),
                         modified_by=profile_id,
                         roles=['administrators'],
                         title='Thumbnail',
                         slug='thumbnail',
                         is_system=True,
                         is_active=True,
                         width=144,
                         height=144)
        dbsession.add(size)
        size = PhotoSize(id=4,
                         created_on=datetime.datetime.now(),
                         created_by=profile_id,
                         modified_on=datetime.datetime.now(),
                         modified_by=profile_id,
                         roles=['administrators'],
                         title='Tiny',
                         slug='tiny',
                         is_system=False,
                         is_active=True,
                         width=240,
                         height=240)
        dbsession.add(size)
        size = PhotoSize(id=5,
                         created_on=datetime.datetime.now(),
                         created_by=profile_id,
                         modified_on=datetime.datetime.now(),
                         modified_by=profile_id,
                         roles=['administrators'],
                         title='Extra Small',
                         slug='extra-small',
                         is_system=False,
                         is_active=True,
                         width=432,
                         height=324)
        dbsession.add(size)
        size = PhotoSize(id=6,
                         created_on=datetime.datetime.now(),
                         created_by=profile_id,
                         modified_on=datetime.datetime.now(),
                         modified_by=profile_id,
                         roles=['administrators'],
                         title='Small',
                         slug='small',
                         is_system=True,
                         is_active=True,
                         width=576,
                         height=432)
        dbsession.add(size)
        size = PhotoSize(id=7,
                         created_on=datetime.datetime.now(),
                         created_by=profile_id,
                         modified_on=datetime.datetime.now(),
                         modified_by=profile_id,
                         roles=['administrators'],
                         title='Medium',
                         slug='medium',
                         is_system=True,
                         is_active=True,
                         width=792,
                         height=594)
        dbsession.add(size)
        size = PhotoSize(id=8,
                         created_on=datetime.datetime.now(),
                         created_by=profile_id,
                         modified_on=datetime.datetime.now(),
                         modified_by=profile_id,
                         roles=['administrators'],
                         title='Large',
                         slug='large',
                         is_system=True,
                         is_active=True,
                         width=1008,
                         height=756)
        dbsession.add(size)
        size = PhotoSize(id=9,
                         created_on=datetime.datetime.now(),
                         created_by=profile_id,
                         modified_on=datetime.datetime.now(),
                         modified_by=profile_id,
                         roles=['administrators'],
                         title='Extra Large',
                         slug='extra-large',
                         is_system=False,
                         is_active=True,
                         width=1224,
                         height=918)
        dbsession.add(size)
        size = PhotoSize(id=10,
                         created_on=datetime.datetime.now(),
                         created_by=profile_id,
                         modified_on=datetime.datetime.now(),
                         modified_by=profile_id,
                         roles=['administrators'],
                         title='Huge',
                         slug='huge',
                         is_system=False,
                         is_active=True,
                         width=1656,
                         height=1242)
        dbsession.add(size)

        album1 = Album(created_on=datetime.datetime.now(),
                       created_by=profile_id,
                       modified_on=datetime.datetime.now(),
                       modified_by=profile_id,
                       roles=['authenticated'],
                       title='Root', slug=slugify.slugify('Root'))
        dbsession.add(album1)

        dbsession.execute('GRANT SELECT ON pg_authid TO PUBLIC;')

        # ALBUM: Setup row level security for the album table
        dbsession.execute("""
            -- Grant permissions to the table
            GRANT SELECT, INSERT, UPDATE, DELETE ON album TO administrators;
            GRANT SELECT ON album TO authenticated, unauthenticated;
            
            GRANT USAGE, SELECT ON SEQUENCE album_id_seq TO authenticated;

            -- Enable row level security
            ALTER TABLE album ENABLE ROW LEVEL SECURITY;

            -- Allow an administrator to do anything
            CREATE POLICY administrators ON album FOR ALL TO administrators
                USING (true)
                WITH CHECK (true);

            -- Allow viewers to select rows on the table if they are
            -- in the proper group
            CREATE POLICY viewers ON album FOR SELECT
                USING (roles && (SELECT ARRAY(SELECT pg_get_userbyid(oid)
                                              FROM pg_authid a 
                                              WHERE pg_has_role(current_user, a.oid, 'member'))::text[]));

            -- Allow the created_by user to SELECT, DELETE, INSERT, UPDATE
            -- for rows they are associated with
            CREATE POLICY created_by ON album FOR ALL
                USING (created_by = current_user)
                WITH CHECK (created_by = current_user);
        """)

        # CONTACT: Setup row level security for the contact table
        dbsession.execute("""
            -- Grant permissions to the table
            GRANT SELECT, INSERT, UPDATE, DELETE ON contact TO administrators;
            GRANT SELECT, INSERT ON contact TO authenticated, unauthenticated;
            
            GRANT USAGE, SELECT ON SEQUENCE contact_id_seq TO authenticated, unauthenticated;

            -- Enable row level security
            ALTER TABLE contact ENABLE ROW LEVEL SECURITY;

            -- Allow an administrator to do anything
            CREATE POLICY administrators ON contact FOR ALL TO administrators
                USING (true)
                WITH CHECK (true);

            -- Allow an unauthenticated to do insert a row
            CREATE POLICY add_record ON contact FOR INSERT TO unauthenticated
                WITH CHECK (true);

            -- Allow viewers to select rows on the table if they are
            -- in the proper group
            CREATE POLICY viewers ON contact FOR SELECT
                USING (roles && (SELECT ARRAY(SELECT pg_get_userbyid(oid)
                                              FROM pg_authid a 
                                              WHERE pg_has_role(current_user, a.oid, 'member'))::text[]));
        """)

        # NAVIGATION: Setup row level security for the navigation table
        dbsession.execute("""
            -- Grant permissions to the table
            GRANT SELECT, INSERT, UPDATE, DELETE ON navigation TO administrators;
            GRANT SELECT ON navigation TO authenticated, unauthenticated;

            -- Enable row level security
            ALTER TABLE navigation ENABLE ROW LEVEL SECURITY;

            -- Allow an administrator to do anything
            CREATE POLICY administrators ON navigation FOR ALL TO administrators
                USING (true)
                WITH CHECK (true);

            -- Allow viewers to select rows on the table if they are
            -- in the proper group
            CREATE POLICY viewers ON navigation FOR SELECT
                USING (roles && (SELECT ARRAY(SELECT pg_get_userbyid(oid)
                                              FROM pg_authid a 
                                              WHERE pg_has_role(current_user, a.oid, 'member'))::text[]));
        """)

        # PHOTO: Setup row level security for the photo table
        dbsession.execute("""
            -- Grant permissions to the table
            GRANT SELECT, INSERT, UPDATE, DELETE ON photo TO administrators;
            GRANT SELECT ON photo TO authenticated, unauthenticated;
            
            GRANT USAGE, SELECT ON SEQUENCE photo_id_seq TO authenticated;

            -- Enable row level security
            ALTER TABLE photo ENABLE ROW LEVEL SECURITY;

            -- Allow an administrator to do anything
            CREATE POLICY administrators ON photo FOR ALL TO administrators
                USING (true)
                WITH CHECK (true);

            -- Allow viewers to select rows on the table if they are
            -- in the proper group
            CREATE POLICY viewers ON photo FOR SELECT
                USING (roles && (SELECT ARRAY(SELECT pg_get_userbyid(oid)
                                              FROM pg_authid a 
                                              WHERE pg_has_role(current_user, a.oid, 'member'))::text[]));

            -- Allow the created_by user to SELECT, DELETE, INSERT, UPDATE
            -- for rows they are associated with
            CREATE POLICY created_by ON photo FOR ALL
                USING (created_by = current_user)
                WITH CHECK (created_by = current_user);
        """)

        # SETTING: Setup row level security for the setting table
        dbsession.execute("""
            -- Grant permissions to the table
            GRANT SELECT, INSERT, UPDATE, DELETE ON setting TO administrators;
            GRANT SELECT ON setting TO authenticated, unauthenticated;

            -- Enable row level security
            ALTER TABLE setting ENABLE ROW LEVEL SECURITY;

            -- Allow an administrator to do anything
            CREATE POLICY administrators ON setting FOR ALL TO administrators
                USING (true)
                WITH CHECK (true);
        """)

        # TASK: Setup row level security for the task table
        dbsession.execute("""
            -- Grant permissions to the table
            GRANT SELECT, INSERT, UPDATE, DELETE ON task TO administrators;
            GRANT SELECT ON task TO authenticated, unauthenticated;

            -- Enable row level security
            ALTER TABLE task ENABLE ROW LEVEL SECURITY;

            -- Allow an administrator to do anything
            CREATE POLICY administrators ON task FOR ALL TO administrators
                USING (true)
                WITH CHECK (true);
        """)

        # PROFILE: Setup row level security for the profile table
        dbsession.execute("""
            -- Grant permissions to the table
            GRANT SELECT, INSERT, UPDATE, DELETE ON profile TO administrators;
            GRANT SELECT ON profile TO authenticated, unauthenticated;

            -- Enable row level security
            ALTER TABLE profile ENABLE ROW LEVEL SECURITY;

            -- Allow an administrator to do anything
            CREATE POLICY administrators ON profile FOR ALL TO administrators
                USING (true)
                WITH CHECK (true);

            -- Allow viewers to select rows on the table if they are
            -- in the proper group
            CREATE POLICY viewers ON profile FOR SELECT
                USING (roles && (SELECT ARRAY(SELECT pg_get_userbyid(oid)
                                              FROM pg_authid a 
                                              WHERE pg_has_role(current_user, a.oid, 'member'))::text[]));

            -- Allow the user to SELECT, UPDATE
            -- for their own record
            CREATE POLICY created_by ON profile FOR ALL
                USING (username = current_user)
                WITH CHECK (username = current_user);
        """)

        # PROFILE_GROUP: Setup row level security for the profile_group table
        dbsession.execute("""
            -- Grant permissions to the table
            GRANT SELECT, INSERT, UPDATE, DELETE ON profile_group TO administrators;
            GRANT SELECT ON profile_group TO authenticated, unauthenticated;

            -- Enable row level security
            ALTER TABLE profile_group ENABLE ROW LEVEL SECURITY;

            -- Allow an administrator to do anything
            CREATE POLICY administrators ON profile_group FOR ALL TO administrators
                USING (true)
                WITH CHECK (true);

            -- Allow viewers to select rows on the table if they are
            -- in the proper group
            CREATE POLICY viewers ON profile_group FOR SELECT
                USING (roles && (SELECT ARRAY(SELECT pg_get_userbyid(oid)
                                              FROM pg_authid a 
                                              WHERE pg_has_role(current_user, a.oid, 'member'))::text[]));
        """)

        # PHOTO_ALBUM: Setup row level security for the photo_album table
        dbsession.execute("""
            -- Grant permissions to the table
            GRANT SELECT, INSERT, UPDATE, DELETE ON photo_album TO administrators;
            GRANT SELECT ON photo_album TO authenticated, unauthenticated;

            -- Enable row level security
            ALTER TABLE photo_album ENABLE ROW LEVEL SECURITY;

            -- Allow an administrator to do anything
            CREATE POLICY administrators ON photo_album FOR ALL TO administrators
                USING (true)
                WITH CHECK (true);
        """)

        # PHOTO_TAG: Setup row level security for the photo_tag table
        dbsession.execute("""
            -- Grant permissions to the table
            GRANT SELECT, INSERT, UPDATE, DELETE ON photo_tag TO administrators;
            GRANT SELECT ON photo_tag TO authenticated, unauthenticated;

            -- Enable row level security
            ALTER TABLE photo_tag ENABLE ROW LEVEL SECURITY;

            -- Allow an administrator to do anything
            CREATE POLICY administrators ON photo_tag FOR ALL TO administrators
                USING (true)
                WITH CHECK (true);
        """)

        # TAG: Setup row level security for the tag table
        dbsession.execute("""
            -- Grant permissions to the table
            GRANT SELECT, INSERT, UPDATE, DELETE ON tag TO administrators;
            GRANT SELECT ON tag TO authenticated, unauthenticated;

            GRANT USAGE, SELECT ON SEQUENCE tag_id_seq TO authenticated;

            -- Enable row level security
            ALTER TABLE tag ENABLE ROW LEVEL SECURITY;

            -- Allow an administrator to do anything
            CREATE POLICY administrators ON tag FOR ALL TO administrators
                USING (true)
                WITH CHECK (true);
        """)

        # PHOTO_SIZE: Setup row level security for the photo_size table
        dbsession.execute("""
            -- Grant permissions to the table
            GRANT SELECT, INSERT, UPDATE, DELETE ON photo_size TO administrators;
            GRANT SELECT ON photo_size TO authenticated;

            -- Enable row level security
            ALTER TABLE photo_size ENABLE ROW LEVEL SECURITY;

            -- Allow an administrator to do anything
            CREATE POLICY administrators ON photo_size FOR ALL TO administrators
                USING (true)
                WITH CHECK (true);
        """)

        # PHOTO_FILE: Setup row level security for the photo_file table
        dbsession.execute("""
            -- Grant permissions to the table
            GRANT SELECT, INSERT, UPDATE, DELETE ON photo_file TO administrators;
            GRANT SELECT ON photo_file TO authenticated, unauthenticated;
            
            GRANT USAGE, SELECT ON SEQUENCE photo_file_id_seq TO authenticated;

            -- Enable row level security
            ALTER TABLE photo_file ENABLE ROW LEVEL SECURITY;

            -- Allow an administrator to do anything
            CREATE POLICY administrators ON photo_file FOR ALL TO administrators
                USING (true)
                WITH CHECK (true);
        """)
