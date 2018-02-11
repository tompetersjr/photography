from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPFound,
)
from pyramid.security import (
    authenticated_userid,
)
from pyramid.view import forbidden_view_config


def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('landscapes', '/landscapes')
    config.add_route('family', '/family')
    config.add_route('album', '/album/{album}')
    config.add_route('about', '/about')
    config.add_route('contact', '/contact')
    config.add_route('admin-dashboard', '/admin/dashboard')
    config.add_route('admin-users', '/admin/users')
    config.add_route('admin-roles', '/admin/roles')
    config.add_route('faq', '/faq')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('upload', '/upload')
    config.add_route('image', '/image/{size}/{title}')

    # API
    config.add_route('api-photo-count-by-album', '/api/album-photo-counts')


@forbidden_view_config()
def forbidden_view(request):
    # do not allow a user to login if they are already logged in
    if authenticated_userid(request):
        return HTTPForbidden()

    loc = request.route_url('login', _query=(('next', request.path),))
    return HTTPFound(location=loc)


