# -*- coding: utf-8 -*-
"""
Classi Model per ritornare oggetti SqlAlchemy al posto di semplici json.

Con questi, sarà facile per il programma che usa la libreria salvare
i dati su un database relazionale.
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()


class Media(Base):
    """
    Model che mappa un'immagine (o un video)
    """

    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    height = Column(Integer)
    width = Column(Integer)
    url = Column(String)
    comments = Column(Integer)
    likes = Column(Integer)
    caption = Column(String)
    is_video = Column(Boolean)
    user = Column(Integer)
    unix_datetime = Column(String)
    json = Column(String)
    code = Column(String)

    @hybrid_property
    def created_at(self):
        return datetime.fromtimestamp(int(self.unix_datetime))

    def __repr__(self):
        return "<Image (id='{id}', caption='{caption}')>".format(
            id=self.id, caption=self.caption[:25]
        )


class Comment(Base):
    """
    Model che mappa un commento
    """

    __tablename__ = 'comments'

    id_immagine = Column(Integer, primary_key=True)
    id_commento = Column(Integer, primary_key=True)
    username = Column(String, primary_key=True)
    text = Column(String)
    unix_datetime = Column(String)
    json = Column(String)
    code = Column(String)

    @hybrid_property
    def created_at(self):
        return datetime.fromtimestamp(int(self.unix_datetime))

    def __repr__(self):
        return "<Comment (id='{id}', caption='{text}')>".format(
            id=self.id, text=self.text[:25]
        )
