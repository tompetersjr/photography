from json.decoder import JSONDecodeError
from pyramid.view import view_config, view_defaults

from ..models.album import Album, AlbumSchema


@view_defaults(route_name='api_albums', renderer='json')
class AlbumsView:
    def __init__(self, request):
        # Used by the before_insert and before_update event listeners
        request.dbsession.info['username'] = request.user.username
        self.request = request

    def get(self):
        albums = Album().get_all(self.request.dbsession)
        schema = AlbumSchema(many=True,
                             only=('id', 'parent_id',
                                   'sort_order', 'title', 'slug')
                             )
        result = schema.dump(albums)
        data = result.data
        errors = result.errors

        if errors:
            status = 400
        else:
            status = 200

        return {
            'status': status,
            'data': data,
            'errors': errors
        }

    def post(self):
        data = []
        try:
            data, errors = AlbumSchema().load(self.request.json_body)
        except JSONDecodeError as e:
            errors = {
                'JSON Decode Error': e.msg
            }

        if not errors:
            parent = Album().get_by_id(self.request.dbsession, data['parent_id'])

            new_album = Album(roles=parent.roles, parent=parent,
                              title=data['title'], slug=data['slug'])
            self.request.dbsession.add(new_album)

            schema = AlbumSchema(only=('id', 'parent_id',
                                       'sort_order', 'title', 'slug'))
            result = schema.dump(new_album)
            data = result.data
            errors = result.errors

            if errors:
                status = 400
            else:
                status = 200
        else:
            status = 400

        return {
            'status': status,
            'data': data,
            'errors': errors
        }


@view_defaults(route_name='api_album', renderer='json')
class AlbumView:
    def __init__(self, request):
        # Used by the before_insert and before_update event listeners
        request.dbsession.info['username'] = request.user.username
        self.request = request

    def get(self):
        album = Album().get_album_by_slug(self.request.dbsession,
                                          self.request.matchdict['album'])
        schema = AlbumSchema(only=('id', 'parent_id',
                                   'sort_order', 'title', 'slug'))
        result = schema.dump(album)
        data = result.data
        errors = result.errors

        if errors:
            status = 400
        else:
            status = 200

        return {
            'status': status,
            'data': data,
            'errors': errors
        }

    def put(self):
        album = Album().get_album_by_slug(self.request.dbsession,
                                          self.request.matchdict['album'])

        parent_id = self.request.json_body['parent_id']
        title = self.request.json_body['title']
        slug = self.request.json_body['slug']

        parent = Album().get_by_id(self.request.dbsession, parent_id)

        album.parent = parent
        album.title = title
        album.slug = slug

        self.request.dbsession.add(album)

        schema = AlbumSchema(only=('id', 'parent_id',
                                   'sort_order', 'title', 'slug'))
        result = schema.dump(album)
        data = result.data
        errors = result.errors

        if errors:
            status = 400
        else:
            status = 200

        return {
            'status': status,
            'data': data,
            'errors': errors
        }

    def delete(self):
        album = Album().get_album_by_slug(self.request.dbsession,
                                          self.request.matchdict['album'])

        self.request.dbsession.delete(album)
        return {
            'status': 200,
            'data': [],
            'error': {}
        }


@view_defaults(renderer='json')
class AlbumGraphViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='api-photo-count-by-album')
    def api_photo_count_by_album(self):
        counts = Album().get_photo_counts_by_album(self.request.dbsession)

        labels = []
        data = []
        for item in counts:
            labels.append(item[0])
            data.append(item[1])

        result_size = len(labels)

        backgroung_colors = [
            'rgba(255, 99, 132,  0.2)',
            'rgba(54,  162, 235, 0.2)',
            'rgba(255, 206, 86,  0.2)',
            'rgba(75,  192, 192, 0.2)',
            'rgba(153, 102, 255, 0.2)',
            'rgba(255, 159, 64,  0.2)'
        ]

        border_colors = [
            'rgba(255, 99, 132,  1)',
            'rgba(54,  162, 235, 1)',
            'rgba(255, 206, 86,  1)',
            'rgba(75,  192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64,  1)'
        ]

        chart = {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'data': data,
                    'backgroundColor': backgroung_colors[:result_size],
                    'borderColor': border_colors[:result_size],
                    'borderWidth': 1
                }]
            },
            'options': {
                'title': {
                    'display': False
                },
                'legend': {
                    'display': False
                },
                'scales': {
                    'yAxes': [{
                        'ticks': {
                            'beginAtZero': True
                        }
                    }]
                }
            }
        }

        return chart
