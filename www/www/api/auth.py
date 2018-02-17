import psycopg2

from pyramid.view import view_defaults


@view_defaults(route_name='api_login', renderer='json')
class AuthView:
    def __init__(self, request):
        # Used by the before_insert and before_update event listeners
        self.request = request

    def post(self):
        username = self.request.json_body['login']
        password = self.request.json_body['password']

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
            message = 'Failed login'

        if username:
            return {
                'result': 'ok',
                'token': self.request.create_jwt_token(username)
            }
        else:
            return {
                'result': 'error'
            }