from pyramid.view import (
    view_config,
    view_defaults
)


@view_defaults(route_name='admin', renderer='admin.jinja2')
class AlbumViews:
    def __init__(self, request):
        # Used by the before_insert and before_update event listeners
        request.dbsession.info['username'] = request.user.username
        self.request = request

    @view_config(route_name='admin', renderer='/admin/admin.jinja2')
    def home(self):
        return {
            'page': 'admin',
        }
