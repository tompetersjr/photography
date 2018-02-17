import psycopg2

from pyramid.interfaces import IAuthenticationPolicy
from pyramid.view import view_defaults


@view_defaults(route_name='api_login', renderer='json')
class AuthView:
    def __init__(self, request):
        # Used by the before_insert and before_update event listeners
        self.request = request

    def post(self):
        username = self.request.json_body['login']
        password = self.request.json_body['password']
        error = ''

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
        except psycopg2.OperationalError as e:
            error = 'Failed login'

        if username:
            token = self.request.create_jwt_token(username)
            return {
                'success': True,
                'token': token
            }
        else:
            return {
                'success': False,
                'result': error
            }