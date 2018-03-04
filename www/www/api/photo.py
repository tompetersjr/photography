import slugify
import transaction

from json.decoder import JSONDecodeError
from marshmallow import ValidationError
from pyramid.view import view_defaults
from sqlalchemy.exc import IntegrityError

from ..models.album import Album
from ..models.photo import Photo, PhotoAlbum
from ..schemas import PhotoSchema


# https://philsturgeon.uk/api/2016/01/04/http-rest-api-file-uploads/


@view_defaults(route_name='api_photos', renderer='json')
class PhotosView:
    def __init__(self, request):
        if request.user:
            request.dbsession.info['username'] = request.user.username
        self.request = request

    def get(self):
        photos = Photo().get_all_in_album(self.request.dbsession,
                                          self.request.matchdict.get('id'))
        schema = PhotoSchema(many=True,
                             only=('id', 'title', 'slug',
                                   'caption', 'original_filename',
                                   'created_at', 'camera_make',
                                   'camera_model', 'lens',
                                   'focal_length', 'exposure',
                                   'f_stop', 'height', 'width')
                             )
        data = schema.dump(photos)
        return data

    def post(self):
        try:
            data = PhotoSchema().load(self.request.json_body)
        except JSONDecodeError as e:
            self.request.response.status = 400
            return {
                'JSON Error': [e.msg]
            }
        except ValidationError as err:
            self.request.response.status = 400
            return err.messages

        album = Album().get_by_id(self.request.dbsession, data['album_id'])
        if album is None:
            self.request.response.status = 400
            return {
                'error': ['Bad or Missing `album_id` value']
            }

        sp = transaction.savepoint()
        try:
            slug = slugify.slugify(data['title'])
            new_photo = Photo(roles=album.roles, title=data['title'],
                              slug=slug, caption=data['caption'],
                              original_filename=data['original_filename'])
            self.request.dbsession.add(new_photo)

            photo_album = PhotoAlbum(photo=new_photo,
                                     album=album)
            self.request.dbsession.add(photo_album)

            self.request.dbsession.flush()
        except IntegrityError:
            sp.rollback()
            self.request.response.status = 400
            return {
                'error': ['Photo `slug` and `original_filename` '
                          'must be unique within each album']
            }

        schema = PhotoSchema(only=('id', 'title', 'slug',
                                   'caption', 'original_filename'))
        data = schema.dump(new_photo)
        self.request.response.status = 201
        self.request.response.headers['location'] \
            = 'api/photo/upload?photo_id={}'.format(new_photo.id)
        return data


@view_defaults(route_name='api_photo', renderer='json')
class PhotoView:
    def __init__(self, request):
        if request.user:
            request.dbsession.info['username'] = request.user.username
        self.request = request

    def _validate_photo_id(self, photo_id):
        if not photo_id.isdigit():
            self.request.response.status = 400
            return {
                'error': ['Photo `id` must be a number']
            }

        photo = Photo().get_by_id(self.request.dbsession,
                                  photo_id)

        if photo is None:
            self.request.response.status = 400
            return {
                'error': ['Photo does not exist']
            }

        return photo

    def get(self):
        photo = self._validate_photo_id(self.request.matchdict.get('id'))

        schema = PhotoSchema(only=('id', 'title', 'slug', 'caption',
                                   'original_filename', 'created_at',
                                   'camera_make', 'camera_model', 'lens',
                                   'focal_length', 'exposure', 'f_stop',
                                   'height', 'width'))
        return schema.dump(photo)

    def put(self):
        keys = ['id', 'title', 'slug', 'caption', 'original_filename',
                'created_at', 'camera_make', 'camera_model', 'lens',
                'focal_length', 'exposure', 'f_stop', 'height', 'width']
        for key in keys:
            if key not in self.request.json_body:
                self.request.response.status = 400
                return {
                    'error': ['No `{}` specified'.format(key)]
                }

        photo_id = self.request.matchdict.get('id')
        title = self.request.json_body.get('title')
        slug = self.request.json_body.get('slug')
        caption = self.request.json_body.get('caption')
        original_filename = self.request.json_body.get('original_filename')
        created_at = self.request.json_body.get('created_at')
        camera_make = self.request.json_body.get('camera_make')
        camera_model = self.request.json_body.get('camera_model')
        lens = self.request.json_body.get('lens')
        focal_length = self.request.json_body.get('focal_length')
        exposure = self.request.json_body.get('exposure')
        f_stop = self.request.json_body.get('f_stop')
        height = self.request.json_body.get('height')
        width = self.request.json_body.get('width')

        photo = self._validate_photo_id(photo_id)

        photo.title = title
        photo.slug = slug
        photo.caption = caption
        photo.original_filename = original_filename
        photo.created_at = created_at
        photo.camera_make = camera_make
        photo.camera_model = camera_model
        photo.lens = lens
        photo.focal_length = focal_length
        photo.exposure = exposure
        photo.f_stop = f_stop
        photo.height = height
        photo.width = width

        sp = transaction.savepoint()
        try:
            self.request.dbsession.add(photo)
            self.request.dbsession.flush()
        except IntegrityError:
            sp.rollback()
            self.request.response.status = 400
            return {
                'error': ['Album slug must be unique within each album']
            }

        schema = PhotoSchema(only=('id', 'title', 'slug', 'caption',
                                   'original_filename', 'created_at',
                                   'camera_make', 'camera_model', 'lens',
                                   'focal_length', 'exposure', 'f_stop',
                                   'height', 'width'))
        return schema.dump(photo)

    def delete(self):
        photo_id = self.request.matchdict.get('id')
        photo = self._validate_photo_id(photo_id)

        if photo is None:
            self.request.response.status = 400
            return {
                'error': ['Album does not exist']
            }

        photo_albums = PhotoAlbum().get_by_photo_albums(self.request.dbsession,
                                                        photo_id)
        for item in photo_albums:
            self.request.dbsession.delete(item)

        self.request.dbsession.delete(photo)

        return {
            'success': 'Deleted Photo {}'.format(self.request.matchdict['id'])
        }
