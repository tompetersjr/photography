from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from .models import Profile


def get_user(request):
    username = request.unauthenticated_userid
    if username is not None:
        # We should be caching this.....
        user = request.cache.get('user_{}'.format(username))
        if user is None:
            user = request.dbsession.query(Profile).get(username)
            request.cache.set('user_{}'.format(username), user)
        return user


def includeme(config):
    settings = config.get_settings()
    authn_policy = AuthTktAuthenticationPolicy(
        settings['auth.secret'],
        hashalg='sha512',
    )
    authz_policy = ACLAuthorizationPolicy()

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_request_method(get_user, 'user', reify=True)
