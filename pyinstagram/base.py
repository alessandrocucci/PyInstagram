# -*- coding: utf-8 -*-
from operator import itemgetter

import requests
import time

from .exceptions import OAuthException, PyInstagramException
from .oauth import OAuth
from .constants import API_URL


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
        next_url = ""  # per la paginazione
        res = []
        retry = 1  # serve per ripetere la chiamata dopo un ora se supero il limite di richieste
        while retry:
            res = getattr(requests, method)(uri, data=data)
            res, next_url = self._handle_response(res)
            if res == 0:
                # la chiamata non è andata a buon fine perchè ho raggiunto il limite di chiamate
                # ho già aspettato un'ora, adesso ci riprovo.
                continue
            retry = 0
        return res, next_url

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
            except Exception:
                raise Exception(request.text)
            else:
                data = res['data']
                next_url = res['pagination'].get('next_url')
                return data, next_url

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

    def get_by_user(self, id_user=None, count=0):
        """
        Metodo usato per cercare gli ultimi post di un utente.
        Se non viene passato il paramentro id_user, chiederemo
        i post dell'utente che ha autorizzato l'app.

        :param id_user: str - post dell'utente da cercare
        :param count: int - limita a {count} risultati
        :return: list - lista dati
        """
        all_media = []
        id_user = id_user or "self"
        url = API_URL + "users/{0}/media/recent/?access_token={1}".format(id_user, self.access_token)
        if count:
            url += "&count={}".format(count)
        raw_list, next_url = self._make_request(url)
        all_media.extend(raw_list)
        if len(all_media) > count:
            return all_media[:count]
        while next_url:
            raw_list, next_url = self._make_request(next_url)
            all_media.extend(raw_list)
        return all_media[:count]

    def get_by_hashtag(self, tags=(), count=0):
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
            url = API_URL + "tags/{0}/media/recent?access_token={1}".format(tag, self.access_token)
            if count:
                url += "&count={}".format(count)
            raw_list, next_url = self._make_request(url)
            all_media.extend(raw_list)
            while next_url:
                raw_list, next_url = self._make_request(next_url)
                all_media.extend(raw_list)
        return all_media

    def search_for_tag(self, tag, count=3):
        """
        Metodo usato per cercare hashtag simili a un altro.

        :param tag: str - hashtag da cercare
        :param count: int - limita a un numero di hashtag
        :return: dict
        """
        url = API_URL + "tags/search?q={0}&access_token={1}".format(tag, self.access_token)
        res = self._make_request(url)
        res = sorted(res, key=itemgetter('media_count'))
        names = {r['name']: r['media_count'] for r in res[:count]}
        return names
