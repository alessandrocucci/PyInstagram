# -*- coding: utf-8 -*-
import random
from operator import itemgetter

import requests
import time

from .exceptions import OAuthException, PyInstagramException
from .oauth import OAuth
from .constants import API_URL


class InstagramApiClient(object):
    """
    Classe base per le chiamate all'API ufficiale!
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
                next_url = res.get('pagination', {}).get('next_url')
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
        res, _ = self._make_request(url)
        res = sorted(res, key=itemgetter('media_count'))
        names = {r['name']: r['media_count'] for r in res[:count]}
        return names


class InstagramJsonClient(object):
    """
    Classe per fare semplici richieste in get senza usare access token
    o le API ufficiali. Fa largo uso di url con query string.
    """
    def __init__(self):
        self.base_url = "https://www.instagram.com/"

    def get_by_user(self, user, count=None):
        all_data = []
        base_url = "{base}{user}/media/{{max}}".format(
            base=self.base_url,
            user=user
        )
        max_id = ""
        next_url = base_url.format(max=max_id)
        while True:
            res = requests.get(next_url)
            res = res.json()
            if not res['status'] == "ok":
                return all_data[:count]
            all_data.extend(res['items'])
            if res['items'] and res['more_available'] and (not len(all_data) > count if count else True):
                try:
                    max_id = res['items'][-1]['id']
                    next_url = base_url.format(max="?max_id={}".format(max_id))
                except IndexError:
                    # aspetto un po', index è vuoto e Instagram mi blocca il flusso
                    print(res)
                    time.sleep(random.randint(10, 60))
                else:
                    # tutto ok, ho altri dati da scaricare
                    continue
            else:
                # non ho dati, oppure ne ho di più di quelli voluti
                break
        return all_data[:count]

    def get_by_hashtag(self, tags=(), count=1000000, top_posts=True):
        if isinstance(tags, str):
            tags = (tags, )
        all_data = []
        for tag in tags:
            all_data_tag = []
            base_url = "{base}explore/tags/{tag}?__a=1{{max}}".format(
                base=self.base_url,
                tag=tag
            )
            max_id = ""
            next_url = base_url.format(max=max_id)
            while True:
                res = requests.get(next_url)
                res = res.json()
                media = res['tag']['top_posts']['nodes'] if top_posts else res['tag']['media']['nodes']
                has_next_page = res['tag']['media']['page_info']['has_next_page']
                all_data_tag.extend(media)
                if media and has_next_page and not len(all_data_tag) > count and not top_posts:
                    try:
                        max_id = res['tag']['media']['page_info']['end_cursor']
                        next_url = base_url.format(max="&max_id={}".format(max_id))
                    except IndexError:
                        # aspetto un po', index è vuoto e Instagram mi blocca il flusso
                        time.sleep(random.randint(10, 60))
                    else:
                        # tutto ok, ho altri dati da scaricare
                        continue
                else:
                    # non ho dati, oppure ne ho di più di quelli voluti
                    break
            all_data.extend(all_data_tag)
        return all_data
