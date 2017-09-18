# -*- coding: utf-8 -*-
from operator import itemgetter

import requests
import time

from .exceptions import OAuthException, PyInstagramException
from .oauth import OAuth


class DotDict(dict):
    def __getattr__(self, name):
        return self[name]


class InstagramClient(object):
    """
    Classe base della libreria!
    """
    def __init__(self, access_token=None):
        self.access_token = access_token
        if isinstance(access_token, OAuth):
            self.access_token = access_token.access_token
        if not self.access_token:
            # TODO: Gestire il caso in cui l'access token scada
            raise OAuthException("Per usare la libreria devi prima autenticarti!")

    @staticmethod
    def go_to_sleep(seconds=3600):
        """
        Questo metodo viene chiamato quando è stato raggiunto il
        limite consentito dall'API, se succede metto in pausa il
        programma per un'ora.

        :return: None
        """
        time.sleep(seconds)

    def _make_request(self, uri, method='get', data=None):
        """
        Metodo che effettua la richiesta alle API Instagram.

        :param uri: str - L'Uri da chiamare
        :param method: str - metodo http con cui fare la richiesta
        :param data: dict - dizionario con i dati da passare nella richiesta
        :return: list - lista di dati di risposta
        """
        retry = 1  # serve per ripetere la chiamata dopo un ora se supero il limite di richieste
        res_list = []
        while retry:
            res = getattr(requests, method)(uri, data=data)
            res = self._handle_response(res)
            if isinstance(res, int) and res == 1:
                continue
            retry = 0
            res_list.extend(res)
        return res_list

    def _handle_response(self, request):
        """
        Una volta effettuata la chiamata, ci occupiamo di
        interpretarne la risposta.

        Se la richiesta è andata a buon fine, restituiamo la
        lista dei dati, altrimenti o mettiamo in pausa il
        programma (se abbiamo raggiunto il limite dell'API)
        o solleviamo un'eccezione appropriata.

        :param request: requests - la risposta della chiamata
        :return: list - lista dei dati ricevuti
        """
        if request.status_code == 200:
            # Tutto ok!
            try:
                res = request.json()
                return res['data']
            except Exception:
                raise Exception(request.text)
        elif request.status_code == 429:
            # OAuthRateLimitException
            self.go_to_sleep()
            return 0
        elif request.status_code == 400:
            raise OAuthException(request.json()['meta']['error_message'])
        elif "<!DOCTYPE html>" in request.text:
            raise PyInstagramException("Page not found")
        else:
            raise PyInstagramException

    def get_by_user(self, id_user=None):
        """
        Metodo usato per cercare gli ultimi post di un utente.
        Se non viene passato il paramentro id_user, chiederemo
        i post dell'utente che ha autorizzato l'app.

        :param id_user: str - post dell'utente da cercare
        :return: list - lista dati
        """
        id_user = id_user or "self"
        url = "https://api.instagram.com/v1/" \
              "users/{0}/media/recent/?access_token={1}".format(id_user, self.access_token)
        return self._make_request(url)

    def get_by_hashtag(self, tags=(), count=20):
        """
        Metodo usato per cercare i post con uno o più hashtag.

        :param tags: iterable - gli hashtag da cercare
        :param count: int - massimo numero di risultati da restituire
        :return: list - lista di dati
        """
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
        """
        Metodo usato per cercare hashtag simili a un altro.

        :param tag: str - hashtag da cercare
        :param top: int - limita a un numero di hashtag
        :return: dict
        """
        url = "https://api.instagram.com/v1/tags/search?q={0}&access_token={1}".format(tag, self.access_token)
        res = self._make_request(url)
        res = sorted(res, key=itemgetter('media_count'))
        names = {r['name']: r['media_count'] for r in res[:top]}
        return names
