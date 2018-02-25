from pyramid.view import view_defaults

from ..models.profile import Profile


@view_defaults(route_name='api_login', renderer='json')
class AuthView:
    def __init__(self, request):
        # Used by the before_insert and before_update event listeners
        self.request = request

    def post(self):
        username = self.request.json_body['login']
        password = self.request.json_body['password']

        username = Profile.authorize(username, password)
        if username:
            token = self.request.create_jwt_token(username)
            return {
                'token': token
            }
        else:
            self.request.response.status = 403
            return {
                'error': ['Not Authorized']
            }