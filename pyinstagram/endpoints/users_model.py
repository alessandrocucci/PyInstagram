# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

Base = declarative_base()


class UserCount(Base):
    """
    In questo model mappiamo il numero di post, persone seguite e follower
    di un utente
    """
    __tablename__ = 'user_counts'

    id = Column(Integer, primary_key=True)
    username = Column(String(250), primary_key=True)
    media = Column(Integer)
    follows = Column(Integer)
    followeb_by = Column(Integer)


class User(Base):
    """
    Model che mappa le informazioni di un utente Instagram
    """
    __tablename__ = 'users'

    fk_user = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(Integer, primary_key=True)
    username = Column(String(250), primary_key=True)
    full_name = Column(String(250))
    profile_picture = Column(String(250))
    bio = Column(String(250))
    website = Column(String(250))
    id_usercount = Column(Integer, ForeignKey('user_counts.id'))
    counts = relationship("UserCount")
    type = Column(String(250), server_default="user")


class Image(Base):
    __tablename__ = 'images'
    __table_args__ = {'extend_existing': True}

    url = Column(String(250), primary_key=True)
    id = Column(Integer, autoincrement=True)
    width = Column(Integer)
    height = Column(Integer)


class LowResolution(Base):
    __tablename__ = "images"
    __table_args__ = {'extend_existing': True}

    fk_image = Column(Integer, ForeignKey('images.id'))


class Thumbnail(Base):
    __tablename__ = "images"
    __table_args__ = {'extend_existing': True}

    fk_image = Column(Integer, ForeignKey('images.id'))


class StandardResolution(Base):
    __tablename__ = "images"
    __table_args__ = {'extend_existing': True}

    fk_image = Column(Integer, ForeignKey('images.id'))


class Images(Base):
    __tablename__ = "images"
    __table_args__ = {'extend_existing': True}

    low_resolution = relationship('LowResolution')
    thumbnail = relationship('Thumbnail')
    standard_resolution = relationship('StandardResolution')


class Tag(Base):
    __tablename__ = 'tags'

    fk_tag = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String(250))


class Location(Base):
    __tablename__ = 'media_locations'

    fk_location = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String(250))
    name = Column(String(250))
    latitude = Column(DECIMAL)
    longitude = Column(DECIMAL)
    street_address = Column(String(250))


class Comment(Base):
    __tablename__ = 'media_comments'

    fk_media = Column(String(250), ForeignKey('user_media.id'), primary_key=True)
    count = Column(Integer)


class Like(Base):
    __tablename__ = 'media_likes'

    fk_media = Column(String(250), ForeignKey('user_media.id'), primary_key=True)
    count = Column(Integer)


class Caption(Base):
    __tablename__ = 'media_captions'

    fk_media = Column(String(250), ForeignKey('user_media.id'), primary_key=True)
    id = Column(String(250))
    text = Column(String(250))
    id_user = Column(Integer, ForeignKey('users.id'))
    _from = relationship('User')

    @hybrid_property
    def created_time(self):
        str_value = self.created_time
        return datetime.fromtimestamp(int(str_value)).strftime('%Y-%m-%d %H:%M:%S')

    @created_time.expression
    def datetime(cls):
        dt_column = cls.created_time
        dt_column = func.datetime(dt_column)
        return dt_column


class UserMedia(Base):
    __tablename__ = 'user_media'

    id = Column(String(250), primary_key=True)
    filter = Column(String(250))
    type = Column(String(250))
    created_time = Column(String(250))
    fk_user = Column(Integer, ForeignKey('users.fk_user'))
    link = Column(String(250))
    attribution = Column(String(250))
    fk_location = Column(Integer, ForeignKey('media_locations.fk_location'))
    location = relationship("Location")
    comments = relationship("Comment")
    likes = relationship("Like")
    fk_tags = Column(Integer, ForeignKey('tags.fk_tag'))
    tags = relationship("Tag", order_by="Tag.fk_tag")
    users_in_photo = relationship("User", order_by="User.fk_user")
    fk_image = Column(Integer, ForeignKey('images.id'))
    images = relationship("Images")
