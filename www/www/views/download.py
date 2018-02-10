import tempfile

from libcloud.storage.providers import get_driver
from libcloud.storage.types import Provider
from pyramid.response import FileResponse
from pyramid.view import (
    view_config,
    view_defaults
)

from ..models.photo import Photo, PhotoFile, PhotoSize
from ..models.setting import Setting


@view_defaults(route_name='download', renderer='album.jinja2')
class DownloadViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='image', renderer='album.jinja2')
    def download(self):
        size = self.request.matchdict['size']
        title = self.request.matchdict['title']
        photo_file = self.request.dbsession.query(PhotoFile).\
            join(PhotoFile.photo).\
            join(PhotoFile.photo_size).\
            filter(PhotoSize.slug == size).\
            filter(Photo.original_filename == title).first()

        setting = self.request.dbsession.query(Setting). \
            filter_by(key='storage_path').first()
        cls = get_driver(Provider.LOCAL)
        driver = cls(setting.value)

        obj = driver.get_object(container_name=photo_file.container,
                                object_name=photo_file.filename)

        temporary_file = tempfile.NamedTemporaryFile()
        driver.download_object(obj=obj,
                               destination_path=temporary_file.name,
                               overwrite_existing=True)

        response = FileResponse(temporary_file.name,
                                request=self.request,
                                content_type='image/jpeg')

        return response
