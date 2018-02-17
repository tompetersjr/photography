from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.include('pyramid_jwt')
    config.include('.security')
    config.include('.memcached')
    config.include('.models')
    config.include('.routes')
    config.include('.menu')
    config.include('.site')
    config.include('.celeryconf')
    config.scan()
    return config.make_wsgi_app()
