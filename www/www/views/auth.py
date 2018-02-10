import psycopg2

from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    remember,
    forget,
)

from pyramid.view import (
    view_config,
    view_defaults,
)


@view_defaults(route_name='login', renderer='login.jinja2')
class AuthViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='login', renderer='/home/login.jinja2')
    def login(self):
        next_url = self.request.params.get('next', self.request.referrer)
        if not next_url:
            next_url = self.request.route_url('home')
        message = ''
        if 'form.submitted' in self.request.params:
            username = self.request.POST.get('login', '')
            password = self.request.POST.get('password', '')

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

                username = profile[0]
                headers = remember(self.request, username)
                url = self.request.route_url('home')
                return HTTPFound(location=url, headers=headers)
                #return HTTPFound(location=next_url, headers=headers)
            except psycopg2.OperationalError as e:
                message = 'Failed login'

        return dict(
            message=message,
            url=self.request.route_url('login'),
            next_url=next_url,
        )

    @view_config(route_name='logout')
    def logout(self):
        headers = forget(self.request)
        next_url = self.request.route_url('home')
        return HTTPFound(location=next_url, headers=headers)
