# -*- coding: utf-8 -*-
from operator import itemgetter

import requests
import time

from .oauth import OAuth


class InstagramClient(object):
    """
    Classe principale della libreria!
    """
    def __init__(self, access_token=None):
        self.access_token = access_token
        if isinstance(access_token, OAuth):
            self.access_token = access_token.access_token
        if not self.access_token:
            # TODO: Gestire il caso in cui l'access token scada
            raise Exception("Per usare la libreria devi prima autenticarti!")

    @staticmethod
    def go_to_sleep(seconds=3600):
        """
        Questo metodo viene chiamato quando si riceve una risposta non OK,
        probabilmente si è raggiunto il limite consentito dall'API, o il
        server non è temporaneamente raggiungibile, così metto in pausa
        il programma!
        :return: None
        """
        time.sleep(seconds)

    def _handle_response(self, request):
        if request.status_code == 200:
            # Tutto ok!
            try:
                res = request.json()
                return res['data']
            except Exception:
                raise Exception(request.text)
        elif request.status_code == 429:
            # OAuthRateLimitException
            print("Rate Limit, vado a nanna")
            self.go_to_sleep()
            return []
        else:
            # Scambiato per un bot? La documentazione non mi dice il codice...
            print(request.text)
            self.go_to_sleep()
            return []

    def get_by_user(self, id_user=None):
        id_user = id_user or "self"
        res = requests.get("https://api.instagram.com/v1/"
                           "users/{0}/media/recent/?access_token={1}".format(id_user, self.access_token))
        return self._handle_response(res)

    def get_by_hashtag(self, tags=(), count=20):
        if isinstance(tags, str):
            tags = (tags, )
        all_media = []
        for tag in tags:
            res = requests.get("https://api.instagram.com/v1/"
                               "tags/{0}/media/recent?access_token={1}"
                               "&count={2}".format(tag, self.access_token, count))
            res = self._handle_response(res)
            all_media.extend(res)
        return all_media

    def search_for_tag(self, tag, top=3):
        res = requests.get("https://api.instagram.com/v1/tags/search?q={0}&access_token={1}".format(tag, self.access_token))
        res = self._handle_response(res)
        res = sorted(res, key=itemgetter('media_count'))
        names = {r['name']: r['media_count'] for r in res[:top]}
        return names
