# -*- coding: utf-8 -*-
from operator import itemgetter

import requests
import time

from .exceptions import OAuthException, PyInstagramException
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

    def _make_request(self, uri, method='get', data=None):
        retry = 1  # serve per ripetere la chiamata dopo un ora se supero il limite di richieste
        res = []
        while retry:
            res = getattr(requests, method)(uri, data=data)
            res = self._handle_response(res)
            if isinstance(res, int) and res == 1:
                continue
            retry = 0
        return res

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
            return 0
        elif request.status_code == 400:
            raise OAuthException(request.json()['meta']['error_message'])
        elif "<!DOCTYPE html>" in request.text:
            raise PyInstagramException("Page not found")
        else:
            raise PyInstagramException

    def get_by_user(self, id_user=None):
        id_user = id_user or "self"
        url = "https://api.instagram.com/v1/" \
              "users/{0}/media/recent/?access_token={1}".format(id_user, self.access_token)
        return self._make_request(url)

    def get_by_hashtag(self, tags=(), count=20):
        if isinstance(tags, str):
            tags = (tags, )
        all_media = []
        for tag in tags:
            url = "https://api.instagram.com/v1/" \
                  "tags/{0}/media/recent?access_token={1}" \
                  "&count={2}".format(tag, self.access_token, count)
            res = self._make_request(url)
            all_media.extend(res)
        return all_media

    def search_for_tag(self, tag, top=3):
        url = "https://api.instagram.com/v1/tags/search?q={0}&access_token={1}".format(tag, self.access_token)
        res = self._make_request(url)
        res = sorted(res, key=itemgetter('media_count'))
        names = {r['name']: r['media_count'] for r in res[:top]}
        return names
