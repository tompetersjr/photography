from pyramid.view import (
    view_config,
    view_defaults
)
from sqlalchemy import text
from ..models.album import Album
from ..models.navigation import Navigation
from ..models.photo import Photo, PhotoFile, Tag
from ..models.profile import Profile


@view_defaults(route_name='admin', renderer='admin.jinja2')
class AlbumViews:
    def __init__(self, request):
        # Used by the before_insert and before_update event listeners
        request.dbsession.info['username'] = request.user.username
        self.request = request

    @view_config(route_name='admin-dashboard', renderer='/admin/dashboard.jinja2')
    def dashboard(self):
        admin_menu = Navigation().get_navigation(self.request.dbsession,
                                                 'admin')

        def sizeof_fmt(num, suffix='B'):
            for unit in ['', ':K', ':M', ':G', ':T', ':P', ':E', ':Z']:
                if abs(num) < 1024.0:
                    return "%3.1f%s%s" % (num, unit, suffix)
                num /= 1024.0
            return "%.1f%s%s" % (num, ':Y', suffix)

        album_count = Album().count(self.request.dbsession)
        photo_count = Photo().count(self.request.dbsession)
        tag_count = Tag().count(self.request.dbsession)
        disk_size = PhotoFile().disk_usage(self.request.dbsession)
        if disk_size is not None:
            disk_usage, disk_unit = sizeof_fmt(disk_size).split(':')
        else:
            disk_usage = 0
            disk_unit = 'KB'

        return {
            'page': 'admin-dashboard',
            'album_count': album_count,
            'photo_count': photo_count,
            'tag_count': tag_count,
            'disk_usage': disk_usage,
            'disk_unit': disk_unit,
            'admin_menu': admin_menu
        }

    @view_config(route_name='admin-users', renderer='/admin/users.jinja2')
    def users(self):
        admin_menu = Navigation().get_navigation(self.request.dbsession,
                                                 'admin')

        accounts = Profile().get_all(self.request.dbsession)

        profiles = []
        for account in accounts:
            sql = text("SELECT rolname "
                       "FROM pg_authid a "
                       "WHERE pg_has_role(:username, a.oid, 'member') "
                       "AND rolname NOT LIKE 'pg_%' "
                       "AND rolcanlogin = false "
                       "AND rolname != 'anonymous'"
                       "AND rolname != 'authenticated'"
                       "AND rolname != 'unauthenticated'")
            result = self.request.dbsession.execute(
                sql, {'username': account.username})
            roles = []
            for row in result:
                roles.append(row[0])

            profiles.append({
                'data': account,
                'roles': roles
            })

        return {
            'page': 'admin-users',
            'admin_menu': admin_menu,
            'profiles': profiles
        }

    @view_config(route_name='admin-roles', renderer='/admin/roles.jinja2')
    def roles(self):
        admin_menu = Navigation().get_navigation(self.request.dbsession,
                                                 'admin')

        return {
            'page': 'admin-roles',
            'admin_menu': admin_menu
        }
