# -*- coding: utf-8 -*-
"""

██████╗ ██╗   ██╗██╗███╗   ██╗███████╗████████╗ █████╗  ██████╗ ██████╗  █████╗ ███╗   ███╗
██╔══██╗╚██╗ ██╔╝██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██╔════╝ ██╔══██╗██╔══██╗████╗ ████║
██████╔╝ ╚████╔╝ ██║██╔██╗ ██║███████╗   ██║   ███████║██║  ███╗██████╔╝███████║██╔████╔██║
██╔═══╝   ╚██╔╝  ██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║
██║        ██║   ██║██║ ╚████║███████║   ██║   ██║  ██║╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║
╚═╝        ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝


PyInstagram Library
~~~~~~~~~~~~~~~~~~~

PyInstagram è una libreria Python per il download
di dati Instagram in formato "pythonico"

Esempi di utilizzo:

 >>> from pyinstagram import InstagramJsonClient
 >>> app = InstagramJsonClient()
 >>> media = app.get_by_user("cern", count=1)

 >>> media = app.get_by_hashtag("milanofashionweek")
 >>> for m in media:
 >>>   print(m['display_src'])

"""
from .base import InstagramApiClient, InstagramJsonClient
from .oauth import OAuth

__title__ = 'pyinstagram'
__description__ = 'Instagram HTTP wrapper for Python Developers.'
__version__ = '0.1.6'
__author__ = 'Alessandro Cucci'
__author_email__ = 'alessandro.cucci@gmail.com'
__author_url__ = 'http://www.alessandrocucci.it/'
__license__ = 'MIT'
__copyright__ = 'Copyright 2017 Alessandro Cucci'

__all__ = ['OAuth', 'InstagramApiClient', 'InstagramJsonClient']
