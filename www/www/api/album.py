import transaction

from json.decoder import JSONDecodeError
from marshmallow import ValidationError
from pyramid.view import view_config, view_defaults
from sqlalchemy.exc import IntegrityError

from ..models.album import Album
from ..schemas import AlbumSchema


@view_defaults(route_name='api_albums', renderer='json')
class AlbumsView:
    def __init__(self, request):
        if request.user:
            request.dbsession.info['username'] = request.user.username
        self.request = request

    def get(self):
        albums = Album().get_all(self.request.dbsession)
        schema = AlbumSchema(many=True,
                             only=('id', 'parent_id', 'cover_photo_id',
                                   'sort_order', 'title', 'slug')
                             )
        data = schema.dump(albums)
        return data

    def post(self):
        try:
            data = AlbumSchema().load(self.request.json_body)
        except JSONDecodeError as e:
            self.request.response.status = 400
            return {
                'JSON Error': [e.msg]
            }
        except ValidationError as err:
            self.request.response.status = 400
            return err.messages

        parent = Album().get_by_id(self.request.dbsession, data['parent_id'])
        if parent is None:
            self.request.response.status = 400
            return {
                'error': ['Bad or Missing `parent_id` value']
            }

        sp = transaction.savepoint()
        try:
            new_album = Album(roles=parent.roles, parent=parent,
                              title=data['title'], slug=data['slug'])
            self.request.dbsession.add(new_album)
            self.request.dbsession.flush()
        except IntegrityError:
            sp.rollback()
            self.request.response.status = 400
            return {
                'error': ['Album slug must be unique within each album']
            }

        schema = AlbumSchema(only=('id', 'parent_id', 'cover_photo_id',
                                   'sort_order', 'title', 'slug'))
        data = schema.dump(new_album)
        self.request.response.status = 201
        return data


@view_defaults(route_name='api_album', renderer='json')
class AlbumView:
    def __init__(self, request):
        if request.user:
            request.dbsession.info['username'] = request.user.username
        self.request = request

    def _validate_album_id(self, album_id):
        if not album_id.isdigit():
            self.request.response.status = 400
            return {
                'error': ['Album `id` must be a number']
            }

        album = Album().get_by_id(self.request.dbsession,
                                  album_id)

        if album is None:
            self.request.response.status = 400
            return {
                'error': ['Album does not exist']
            }

        return album

    def get(self):
        album = self._validate_album_id(self.request.matchdict.get('id'))

        schema = AlbumSchema(only=('id', 'parent_id', 'cover_photo_id',
                                   'sort_order', 'title', 'slug'))
        return schema.dump(album)

    def put(self):
        keys = ['id', 'parent_id', 'title', 'slug']
        for key in keys:
            if key not in self.request.json_body:
                self.request.response.status = 400
                return {
                    'error': ['No `{}` specified'.format(key)]
                }

        album_id = self.request.matchdict.get('id')
        parent_id = self.request.json_body.get('parent_id')
        title = self.request.json_body.get('title')
        slug = self.request.json_body.get('slug')

        album = self._validate_album_id(album_id)

        parent = Album().get_by_id(self.request.dbsession, parent_id)
        if parent is None:
            self.request.response.status = 400
            return {
                'error': ['Bad `parent_id` value']
            }

        album.parent = parent
        album.title = title
        album.slug = slug

        sp = transaction.savepoint()
        try:
            self.request.dbsession.add(album)
            self.request.dbsession.flush()
        except IntegrityError:
            sp.rollback()
            self.request.response.status = 400
            return {
                'error': ['Album slug must be unique within each album']
            }

        schema = AlbumSchema(only=('id', 'parent_id', 'cover_photo_id',
                                   'sort_order', 'title', 'slug'))
        return schema.dump(album)

    def delete(self):
        album = self._validate_album_id(self.request.matchdict.get('id'))

        if album is None:
            self.request.response.status = 400
            return {
                'error': ['Album does not exist']
            }

        self.request.dbsession.delete(album)
        return {
            'success': 'Deleted Album {}'.format(self.request.matchdict['id'])
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
