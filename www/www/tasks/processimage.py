import datetime
import json
import tempfile
import uuid
from io import BytesIO

import pyexifinfo
import slugify
from PIL import Image
from libcloud.storage.providers import get_driver
from libcloud.storage.types import Provider, ContainerDoesNotExistError
from sqlalchemy.orm.exc import NoResultFound
from www.celeryconf import app
from www.models.photo import Photo, PhotoFile, PhotoSize, PhotoTag, Tag
from www.models.setting import Setting

from .sqlalchemytask import SqlAlchemyTask


@app.task(base=SqlAlchemyTask, bind=True,
          max_retries=10, default_retry_delay=5)
def processimage(self, photo_slug):
    if photo_slug is None:
        return

    try:
        q = self.dbsession.query(
            Photo, PhotoFile
        ).filter_by(
            slug=photo_slug
        ).join(PhotoFile).first()

        if q is None:
            raise NoResultFound

        photo = q[0]
        photo_file = q[1]

        setting = self.dbsession.query(Setting). \
            filter_by(key='storage_path').first()
        cls = get_driver(Provider.LOCAL)
        driver = cls(setting.value)

        obj = driver.get_object(container_name=photo_file.container,
                                object_name=photo_file.filename)

        temporary_file = tempfile.NamedTemporaryFile()
        driver.download_object(obj=obj,
                               destination_path=temporary_file.name,
                               overwrite_existing=True)

        meta = pyexifinfo.information(temporary_file.name)
        photo.meta = json.dumps(meta)

        if 'EXIF:CreateDate' in meta:
            try:
                photo.created_at = datetime.datetime.strptime(
                    meta['EXIF:CreateDate'],
                    '%Y:%m:%d %H:%M:%S')
            except:
                pass
        if 'EXIF:Make' in meta:
            photo.camera_make = meta['EXIF:Make']
        if 'EXIF:Model' in meta:
            photo.camera_model = meta['EXIF:Model']
        if 'EXIF:LensModel' in meta:
            photo.lens = meta['EXIF:LensModel']
        if 'EXIF:FocalLength' in meta:
            photo.focal_length = meta['EXIF:FocalLength']
        if 'EXIF:ExposureTime' in meta:
            photo.exposure = meta['EXIF:ExposureTime']
        if 'EXIF:FNumber' in meta:
            photo.f_stop = meta['EXIF:FNumber']
        if 'EXIF:ImageDescription' in meta:
            photo.caption = meta['EXIF:ImageDescription']
        if 'File:ImageHeight' in meta:
            photo.height = meta['File:ImageHeight']
        if 'File:ImageWidth' in meta:
            photo.width = meta['File:ImageWidth']

        keywords = None
        if 'IPTC:Keywords' in meta:
            keywords = meta['IPTC:Keywords']
            if isinstance(keywords, str):
                keywords = [keywords]

        if keywords:
            for keyword in keywords:
                tag = self.dbsession.query(Tag).\
                    filter_by(title=keyword).first()
                if tag is None:
                    tag = Tag(created_by=photo_file.created_by,
                              modified_by=photo_file.modified_by,
                              roles=photo.roles,
                              title=keyword)
                    self.dbsession.add(tag)
                    photo_tag = PhotoTag(tag=tag,
                                         photo=photo)
                    self.dbsession.add(photo_tag)
                else:
                    photo_tag = PhotoTag(tag=tag,
                                         photo=photo)
                    self.dbsession.add(photo_tag)

        with Image.open(temporary_file) as im:
            sizes = self.dbsession.query(PhotoSize).\
                filter(PhotoSize.id != 1).all()
            for size in sizes:
                try:
                    container = driver.get_container(
                        container_name=photo_file.container)
                except ContainerDoesNotExistError:
                    container = driver.create_container(
                        container_name=photo_file.container)

                basewidth = size.width
                wpercent = (basewidth / float(im.size[0]))
                hsize = int((float(im.size[1]) * float(wpercent)))
                im2 = im.resize((basewidth, hsize), Image.ANTIALIAS)
                iterator = BytesIO()
                im2.save(iterator, im.format)

                unique_filename = '{}.jpg'.format(uuid.uuid4())

                container.upload_object_via_stream(
                    iterator=BytesIO(iterator.getvalue()),
                    object_name=unique_filename)

                photo_resize_file = PhotoFile(
                    created_by=photo_file.created_by,
                    modified_by=photo_file.modified_by,
                    roles=photo.roles,
                    photo=photo,
                    photo_size=size,
                    container=photo_file.container,
                    filename=unique_filename,
                    file_size=iterator.tell())
                self.dbsession.add(photo_resize_file)

                print('{}x{} {}/{}'.format(size.width,
                                           size.height,
                                           photo_resize_file.container,
                                           photo_resize_file.filename))

        temporary_file.close()

    except NoResultFound as exc:
        raise processimage.retry(exc=exc)
