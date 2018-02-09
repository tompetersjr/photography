import uuid

import slugify
from libcloud.storage.providers import get_driver
from libcloud.storage.types import Provider, ContainerDoesNotExistError
from pyramid.view import (
    view_config,
    view_defaults
)

from ..models.album import Album
from ..models.photo import Photo, PhotoAlbum, PhotoFile
from ..models.setting import Setting
from ..tasks.processimage import processimage


@view_defaults(route_name='albums', renderer='album.jinja2')
class AlbumViews:
    def __init__(self, request):
        # Used by the before_insert and before_update event listeners
        request.dbsession.info['username'] = request.user.username
        self.request = request

    @view_config(route_name='album', renderer='album.jinja2')
    def home(self):
        album = Album().get_album_by_slug(self.request.dbsession,
                                          self.request.matchdict['album'])
        albums = album.children
        photos = album.photos
        breadcrumbs = album.get_breadcrumbs(self.request.dbsession,
                                            self.request.matchdict['album'])

        if 'form.new.album.submitted' in self.request.params:
            title = self.request.params['title']
            slug = slugify.slugify(title)
            new_album = Album(roles=album.roles, parent=album,
                              title=title, slug=slug)
            self.request.dbsession.add(new_album)

        if 'form..upload.photos.submitted' in self.request.params:
            for name, fieldStorage in self.request.POST.items():
                if hasattr(fieldStorage, 'filename'):
                    setting = self.request.dbsession.query(Setting).\
                        filter_by(key='storage_path').first()
                    cls = get_driver(Provider.LOCAL)
                    driver = cls(setting.value)

                    # Create a container if it doesn't already exist
                    container_name = 'images'
                    try:
                        container = driver.get_container(container_name=container_name)
                    except ContainerDoesNotExistError:
                        container = driver.create_container(container_name=container_name)

                    unique_filename = '{}.jpg'.format(uuid.uuid4())

                    driver.upload_object_via_stream(iterator=fieldStorage.file,
                                                    container=container,
                                                    object_name=unique_filename)

                    fieldStorage.file.seek(0, 2)
                    file_size = fieldStorage.file.tell()
                    slug = slugify.slugify(fieldStorage.filename)

                    photo = Photo(roles=album.roles,
                                  title=fieldStorage.filename,
                                  slug=slug,
                                  original_filename=fieldStorage.filename)
                    self.request.dbsession.add(photo)

                    photo_file = PhotoFile(roles=album.roles,
                                           photo=photo,
                                           photo_size_id=1,
                                           container=container_name,
                                           filename=unique_filename,
                                           file_size=file_size)
                    self.request.dbsession.add(photo_file)

                    photo_album = PhotoAlbum(photo=photo,
                                             album=album)
                    self.request.dbsession.add(photo_album)

                    processimage.delay(photo.slug)

        return {
            'page': 'albums',
            'album': album,
            'albums': albums,
            'photos': photos,
            'breadcrumbs': breadcrumbs,
            'url': self.request.route_url('album',
                                          album=self.request.matchdict['album']),
        }
