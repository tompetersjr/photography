from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship, backref

from .meta import Base


class PhotoAlbum(Base):
    __tablename__ = 'photo_album'

    photo_id = Column(Integer, ForeignKey('photo.id'),
                      primary_key=True)
    album_id = Column(Integer, ForeignKey('album.id'),
                      primary_key=True)
    photo = relationship('Photo', backref=backref('albums_assoc'))
    album = relationship('Album', backref=backref('photos_assoc'))

    def __repr__(self):
        return '<PhotoAlbum: {} - {}>'.format(self.photo.title,
                                              self.album.album)


class PhotoTag(Base):
    __tablename__ = 'photo_tag'

    photo_id = Column(Integer, ForeignKey('photo.id'),
                      primary_key=True)
    tag_id = Column(Integer, ForeignKey('tag.id'),
                    primary_key=True)
    photo = relationship('Photo', backref=backref('tags_assoc'))
    tag = relationship('Tag', backref=backref('photos_assoc'))

    def __repr__(self):
        return '<PhotoTag: {} - {}>'.format(self.photo.title,
                                            self.tag.title)


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime(timezone=True), nullable=False)
    created_by = Column(Text, ForeignKey('profile.username'),
                        nullable=False)
    modified_on = Column(DateTime(timezone=True), nullable=False)
    modified_by = Column(Text, ForeignKey('profile.username'),
                         nullable=False)
    roles = Column(ARRAY(Text))
    title = Column(Text, nullable=False)
    created_by_user = relationship('Profile', foreign_keys=[created_by])
    modified_by_user = relationship('Profile', foreign_keys=[modified_by])
    photos = relationship('Photo', secondary='photo_tag')

    def __repr__(self):
        return '<Tag: {}>'.format(self.title)


class PhotoSize(Base):
    __tablename__ = 'photo_size'

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime(timezone=True), nullable=False)
    created_by = Column(Text, ForeignKey('profile.username'),
                        nullable=False)
    modified_on = Column(DateTime(timezone=True), nullable=False)
    modified_by = Column(Text, ForeignKey('profile.username'),
                         nullable=False)
    roles = Column(ARRAY(Text))
    title = Column(Text, nullable=False)
    slug = Column(Text, nullable=False, unique=True)
    is_system = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=False)
    width = Column(Integer)
    height = Column(Integer)
    created_by_user = relationship('Profile', foreign_keys=[created_by])
    modified_by_user = relationship('Profile', foreign_keys=[modified_by])

    def __repr__(self):
        return '<PhotoSize: {} - {}x{}>'.format(self.title,
                                                self.width,
                                                self.height)


class PhotoFile(Base):
    __tablename__ = 'photo_file'

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime(timezone=True), nullable=False)
    created_by = Column(Text, ForeignKey('profile.username'),
                        nullable=False)
    modified_on = Column(DateTime(timezone=True), nullable=False)
    modified_by = Column(Text, ForeignKey('profile.username'),
                         nullable=False)
    photo_id = Column(Integer, ForeignKey('photo.id'), nullable=False)
    photo_size_id = Column(Integer, ForeignKey('photo_size.id'),
                           nullable=False)
    roles = Column(ARRAY(Text))
    container = Column(Text, nullable=False)
    filename = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=False)
    created_by_user = relationship('Profile', foreign_keys=[created_by])
    modified_by_user = relationship('Profile', foreign_keys=[modified_by])
    photo_size = relationship('PhotoSize', foreign_keys=[photo_size_id])
    photo = relationship('Photo', foreign_keys=[photo_id])

    def __repr__(self):
        return '<PhotoFile: {}/{}>'.format(self.container, self.filename)


class Photo(Base):
    __tablename__ = 'photo'

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime(timezone=True), nullable=False)
    created_by = Column(Text, ForeignKey('profile.username'),
                        nullable=False)
    modified_on = Column(DateTime(timezone=True), nullable=False)
    modified_by = Column(Text, ForeignKey('profile.username'),
                         nullable=False)
    roles = Column(ARRAY(Text))
    title = Column(Text, nullable=False)
    slug = Column(Text, nullable=False)
    caption = Column(Text)
    original_filename = Column(Text, nullable=False)
    created_at = Column(DateTime())
    camera_make = Column(Text)
    camera_model = Column(Text)
    lens = Column(Text)
    focal_length = Column(Text)
    exposure = Column(Text)
    f_stop = Column(Text)
    height = Column(Text)
    width = Column(Text)
    meta = Column(JSONB)
    created_by_user = relationship('Profile',
                                   foreign_keys=[created_by])
    modified_by_user = relationship('Profile',
                                    foreign_keys=[modified_by])
    albums = relationship('Album', secondary='photo_album')
    tags = relationship('Tag', secondary='photo_tag')

    def __repr__(self):
        return '<Photo: {}>'.format(self.title)
