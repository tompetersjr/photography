from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship, backref

from .meta import Base


class Album(Base):
    __tablename__ = 'album'

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime(timezone=True), nullable=False)
    created_by = Column(Text, ForeignKey('profile.username'), nullable=False)
    modified_on = Column(DateTime(timezone=True), nullable=False)
    modified_by = Column(Text, ForeignKey('profile.username'), nullable=False)
    roles = Column(ARRAY(Text))
    parent_id = Column(Integer, ForeignKey("album.id"))
    title = Column(Text, nullable=False)
    slug = Column(Text, nullable=False, unique=True)
    created_by_user = relationship('Profile', foreign_keys=[created_by])
    modified_by_user = relationship('Profile', foreign_keys=[modified_by])
    children = relationship('Album',
                            backref=backref('parent', remote_side=[id]))
    photos = relationship('Photo', secondary='photo_album')

    def __repr__(self):
        return '<Album: {}>'.format(self.title)

    @classmethod
    def get_album_by_slug(cls, session, slug):
        album = session.query(Album).filter_by(slug=slug).first()
        return album

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


