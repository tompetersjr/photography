import memcache


def get_cache(request):
    settings = request.registry.settings
    return memcache.Client([settings['memcached.client']], debug=settings['memcached.debug'])


def includeme(config):
    settings = config.get_settings()

    config.add_request_method(get_cache, 'cache', reify=True)
