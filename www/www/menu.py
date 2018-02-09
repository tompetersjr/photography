from .models.navigation import Navigation


def get_navigation(request):
    username = 'anonymous'
    if request.user:
        username = request.user.username
    main_menu = request.cache.get('menu_main_{}'.format(username))
    if main_menu is None:
        main_menu = Navigation().get_navigation(request.dbsession, 'main')

        for nav in main_menu:
            if nav.params is None:
                nav.params = {}

        request.cache.set('menu_main_{}'.format(username), main_menu)

    return main_menu


def includeme(config):
    config.add_request_method(get_navigation, 'main_menu', reify=True)
