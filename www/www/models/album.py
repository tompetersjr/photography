from marshmallow import Schema, fields
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref

from .meta import Base

from .photo import Photo, PhotoAlbum


class AlbumSchema(Schema):
    id = fields.Int()
    created_on = fields.DateTime()
    create_by = fields.Str()
    modified_on = fields.DateTime()
    modified_by = fields.Str()
    parent_id = fields.Int()
    cover_photo_id = fields.Int()
    sort_order = fields.Int()
    title = fields.Str()
    slug = fields.Str()


class Album(Base):
    __tablename__ = 'album'

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime(timezone=True), nullable=False)
    created_by = Column(Text, ForeignKey('profile.username'), nullable=False)
    modified_on = Column(DateTime(timezone=True), nullable=False)
    modified_by = Column(Text, ForeignKey('profile.username'), nullable=False)
    roles = Column(ARRAY(Text))
    parent_id = Column(Integer, ForeignKey("album.id"))
    cover_photo_id = Column(Integer, ForeignKey('photo.id'))
    sort_order = Column(Integer)
    title = Column(Text, nullable=False)
    slug = Column(Text, nullable=False)
    created_by_user = relationship('Profile', foreign_keys=[created_by])
    modified_by_user = relationship('Profile', foreign_keys=[modified_by])
    children = relationship('Album',
                            backref=backref('parent', remote_side=[id]))
    photos = relationship('Photo', secondary='photo_album',
                          order_by='Photo.created_at')

    def __repr__(self):
        return '<Album: {}>'.format(self.title)

    @classmethod
    def get_by_id(cls, session, album_id):
        return session.query(Album).get(album_id)

    @classmethod
    def get_all(cls, session):
        return session.query(Album).all()

    @classmethod
    def get_album_by_slug(cls, session, slug):
        album = session.query(Album).filter_by(slug=slug).first()
        return album

    @classmethod
    def count(cls, session):
        count = session.query(Album).count() - 1  # Skip Root
        return count

    @classmethod
    def get_breadcrumbs(cls, session, slug):
        results = []
        album = session.query(Album).filter_by(slug=slug).first()
        results.append(album)
        if album:
            if album.parent:
                results = cls._get_parent(cls, results)

        return list(reversed(results))

    def _get_parent(self, results):
        index = len(results) - 1
        if results[index].parent:
            album = results[index].parent
            results.append(album)
            return self._get_parent(self, results)

        return results

    @classmethod
    def get_photo_counts_by_album(cls, session, top_num=5):
        if top_num > 5:
            raise ValueError('You can only return up to 5 results.')

        result = session.query(Album.title,
                               func.count(Photo.id).label('Count')).\
            join(PhotoAlbum).\
            join(Photo).\
            filter(Album.slug != 'root').\
            group_by(Album.title).\
            order_by(func.count(Photo.id).desc()).\
            limit(top_num).\
            all()
        return result
