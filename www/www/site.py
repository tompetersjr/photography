def get_site(request):
    settings = request.registry.settings
    return {
        'name': settings['site.name'],
        'photographer': settings['site.photographer'],
        'contact': settings['site.contact'],
    }


def includeme(config):
    config.add_request_method(get_site, 'site', reify=True)
