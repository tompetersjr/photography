from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_jwt import create_jwt_authentication_policy
from pyramid_multiauth import MultiAuthenticationPolicy
from pyramid_multiauth import MultiAuthPolicySelected

from .models import Profile


def includeme(config):
    settings = config.get_settings()

    config.set_authorization_policy(ACLAuthorizationPolicy())

    policy_cookie = AuthTktAuthenticationPolicy(
            settings['auth.secret'],
            hashalg='sha512',
        )
    policy_jwt = create_jwt_authentication_policy(
            config,
            settings['auth.secret'])

    policies = [
        policy_cookie,
        policy_jwt
    ]
    authn_policy = MultiAuthenticationPolicy(policies)
    config.set_authentication_policy(authn_policy)

    def get_user(request):
        import pdb; pdb.set_trace()
        username = request.unauthenticated_userid
        if username is not None:
            # We should be caching this.....
            user = request.cache.get('user_{}'.format(username))
            if user is None:
                user = request.dbsession.query(Profile).get(username)
                request.cache.set('user_{}'.format(username), user)
            return user

    def request_create_token(request, principal, expiration=None, **claims):
        return policy_jwt.create_token(principal, expiration, **claims)

    def request_claims(request):
        return policy_jwt.get_claims(request)

    config.add_request_method(request_create_token, 'create_jwt_token')
    config.add_request_method(request_claims, 'jwt_claims', reify=True)
    config.add_request_method(get_user, 'user', reify=True)
