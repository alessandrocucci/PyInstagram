# -*- coding: utf-8 -*-
import random
from datetime import datetime
from operator import itemgetter

import requests
import time

from pyinstagram.model import Media
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

        :param seconds: int - Numero di secondi di attesa
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

    def get_by_user(self, user, count=None, since=None, until=None):
        """
        Ricerca post (pubblici) di un utente.
        Gestisce automaticamente la paginazione.

        Ritorna una lista di dizionari così composta:
        [
            {
                id: "1606977067425770236_528817151",
                code: "BZNISDyHKr8",
                user: {
                    id: "528817151",
                    full_name: "NASA",
                    profile_picture: "https://scontent-mxp1-1.cdninstagram.com/t51.2885-19/11375151_392132304319140_1291663475_a.jpg",
                    username: "nasa"
                },
                images: {
                    thumbnail: {
                        width: 150,
                        height: 150,
                        url: "https://scontent-mxp1-1.cdninstagram.com/t51.2885-15/s150x150/e15/21690201_1801206810171539_7249344908006260736_n.jpg"
                    },
                    low_resolution: {
                        width: 320,
                        height: 320,
                        url: "https://scontent-mxp1-1.cdninstagram.com/t51.2885-15/s320x320/e15/21690201_1801206810171539_7249344908006260736_n.jpg"
                    },
                    standard_resolution: {
                        width: 640,
                        height: 640,
                        url: "https://scontent-mxp1-1.cdninstagram.com/t51.2885-15/s640x640/e15/21690201_1801206810171539_7249344908006260736_n.jpg"
                    }
                },
                created_time: "1505786616",
                caption: {
                    id: "17887172635109592",
                    text: "Look up in the sky tonight and see Saturn! This month Saturn is the only prominent evening planet low in the southwest sky. Look for it near the constellation Sagittarius. Above and below Saturn--from a dark sky--you can't miss the summer Milky Way spanning the sky from northeast to southwest! Grab a pair of binoculars and scan the teapot-shaped Sagittarius, where stars and some brighter clumps appear as steam from the teapot. Those bright clumps are near the center of our galaxy, which is full of gas, dust and stars. Credit: NASA #nasa #space #astronomy #september #whatsup #night #nightsky #stars #stargazing #saturn #planet",
                    created_time: "1505786616",
                    from: {
                        id: "528817151",
                        full_name: "NASA",
                        profile_picture: "https://scontent-mxp1-1.cdninstagram.com/t51.2885-19/11375151_392132304319140_1291663475_a.jpg",
                        username: "nasa"
                    }
                },
                user_has_liked: false,
                likes: {
                    data: [
                        {
                            id: "4010977557",
                            full_name: "Natalia",
                            profile_picture: "https://scontent-mxp1-1.cdninstagram.com/t51.2885-19/s150x150/14482183_140565769737733_5249004653428867072_a.jpg",
                            username: "nata.barata"
                        },
                        {
                            id: "2055640911",
                            full_name: "S@brin@ Lec○cq ♡☆♡",
                            profile_picture: "https://scontent-mxp1-1.cdninstagram.com/t51.2885-19/s150x150/13534211_1557747037863158_1773299287_a.jpg",
                            username: "melsab19"
                        },
                        {
                            id: "752521983",
                            full_name: "Laura Álvarez Peláez",
                            profile_picture: "https://scontent-mxp1-1.cdninstagram.com/t51.2885-19/10624147_809215025765686_985825156_a.jpg",
                            username: "lauriwushu"
                        },
                        {
                            id: "1719376530",
                            full_name: "Julia Paniti",
                            profile_picture: "https://scontent-mxp1-1.cdninstagram.com/t51.2885-19/10985984_1575721159312127_239135761_a.jpg",
                            username: "julia_paniti"
                        }
                    ],
                    count: 204038
                },
                comments: {
                    data: [
                        {
                            id: "17876620534138631",
                            text: "@jennytried ❤️",
                            created_time: "1505855823",
                            from: {
                                id: "4610349",
                                full_name: "",
                                profile_picture: "https://scontent-mxp1-1.cdninstagram.com/t51.2885-19/10932285_747424172021124_1089839988_a.jpg",
                                username: "siskascherz"
                            }
                        },
                        {
                            id: "17899664473040297",
                            text: "@a.hm.ed.1",
                            created_time: "1505855825",
                            from: {
                                id: "416900232",
                                full_name: "Maryem BenKh",
                                profile_picture: "https://scontent-mxp1-1.cdninstagram.com/t51.2885-19/s150x150/16907969_415736022127336_8841431139366207488_a.jpg",
                                username: "maariam_bk"
                            }
                        },
                        {
                            id: "17871962107174729",
                            text: "Wonderful 😍",
                            created_time: "1505855872",
                            from: {
                                id: "2982243595",
                                full_name: "Smit Raj",
                                profile_picture: "https://scontent-mxp1-1.cdninstagram.com/t51.2885-19/s150x150/21690360_117321958944805_772082897589895168_n.jpg",
                                username: "smit_raj_"
                            }
                        }
                    ],
                count: 1564
                },
                can_view_comments: true,
                can_delete_comments: false,
                type: "video",
                link: "https://www.instagram.com/p/BZNISDyHKr8/",
                location: null,
                alt_media_url: "https://scontent-mxp1-1.cdninstagram.com/t50.2886-16/21904634_340030459792492_153261372472295424_n.mp4",
                videos: {
                    standard_resolution: {
                        width: 640,
                        height: 640,
                        url: "https://scontent-mxp1-1.cdninstagram.com/t50.2886-16/21904634_340030459792492_153261372472295424_n.mp4"
                    },
                    low_bandwidth: {
                        width: 480,
                        height: 480,
                        url: "https://scontent-mxp1-1.cdninstagram.com/t50.2886-16/21868687_149708205622876_4737472794344816640_n.mp4"
                    },
                    low_resolution: {
                        width: 480,
                        height: 480,
                        url: "https://scontent-mxp1-1.cdninstagram.com/t50.2886-16/21868687_149708205622876_4737472794344816640_n.mp4"
                    }
                },
                video_views: 1012473
            },
        ]
        :param user: str - username Instagram
        :param count: int - limita il numero di risultati
        :param since: str - Risultati a partire da questa data, es. "20170101000000"
        :param until: str - Risultati entro questa data, es. "20171231235959"
        :return:
        """
        if since:
            try:
                since = datetime.strptime(since, "%Y%m%d%H%M%S")
            except ValueError:
                raise ValueError("Il parametro since non è in un formato corretto (es. '20170101000000')")

        if until:
            try:
                until = datetime.strptime(until, "%Y%m%d%H%M%S")
            except ValueError:
                raise ValueError("Il parametro until non è in un formato corretto (es. '20170101000000')")

        all_data = []
        base_url = "{base}{user}/media/{{max}}".format(
            base=self.base_url,
            user=user
        )
        max_id = ""
        next_url = base_url.format(max=max_id)
        while True:
            res = requests.get(next_url)
            try:
                res = res.json()
            except Exception:
                raise PyInstagramException("Impossibile scaricare i dati dall'indirizzo: {}".format(next_url))
            if not res['status'] == "ok":
                return all_data[:count]

            for media_res in res['items']:

                # Instagram non mi permette di cercare per data, però mi fornisce la
                # data di creazione del post in formato Unix Timestamp. Quindi, per
                # gestire il caso in cui volessi solo risultati in un certo intervallo,
                # verifico che il mio post sia stato creato in questo lasso di tempo.

                created_at = int(media_res['created_time'])
                if since and created_at < time.mktime(since.timetuple()):
                    # sono andato troppo indietro, posso uscire
                    return all_data[:count]
                if until and created_at > time.mktime(until.timetuple()):
                    continue
                all_data.append(media_res)

            if res['items'] and res['more_available'] and (not len(all_data) > count if count else True):
                # ho oggetti, ne ho altri da scaricare, e non ho raggiunto il limite di risultati
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

    def get_by_hashtag(self, tags=(), count=1000000, top_posts=True, since=None, until=None):
        """
        Ricerca per hashtag.
        Gestisce automaticamente la paginazione.

        Ritorna una lista di oggetti SqlAlchemy a partire da
        una lista di dizionari fatti come segue:

        [
            {
                comments_disabled: false,
                id: "1607551655901147333",
                dimensions: {
                    height: 640,
                    width: 640
                },
                owner: {
                    id: "981246989"
                },
                thumbnail_src: "https://scontent-mxp1-1.cdninstagram.com/t51.2885-15/e35/21820166_125621088095492_8628217971971457024_n.jpg",
                thumbnail_resources: [
                    {
                        src: "https://scontent-mxp1-1.cdninstagram.com/t51.2885-15/s150x150/e35/21820166_125621088095492_8628217971971457024_n.jpg",
                        config_width: 150,
                        config_height: 150
                    },
                    {
                        src: "https://scontent-mxp1-1.cdninstagram.com/t51.2885-15/s240x240/e35/21820166_125621088095492_8628217971971457024_n.jpg",
                        config_width: 240,
                        config_height: 240
                    },
                    {
                        src: "https://scontent-mxp1-1.cdninstagram.com/t51.2885-15/s320x320/e35/21820166_125621088095492_8628217971971457024_n.jpg",
                        config_width: 320,
                        config_height: 320
                    },
                    {
                        src: "https://scontent-mxp1-1.cdninstagram.com/t51.2885-15/s480x480/e35/21820166_125621088095492_8628217971971457024_n.jpg",
                        config_width: 480,
                        config_height: 480
                    }
                ],
                is_video: false,
                code: "BZPK7bAFDDF",
                date: 1505855112,
                display_src: "https://scontent-mxp1-1.cdninstagram.com/t51.2885-15/e35/21820166_125621088095492_8628217971971457024_n.jpg",
                caption: "Tommy Hilfiger London Fashion Week Spring_Summer 2018 @londonfashionweek @britishfashioncouncil @tommyhilfiger #londonfashionweek#LFW#fashion#paris#fashionblogger#tehran#fashioneditor#fashionweek#style#streetstyle##milan#london#newyork#mfw#lfw#nyfw#vogue#gq#art#love#fashionshow#blogger#life#event#ss2018#instafashion#runway#fashionmoment0#TOMMYNOW",
                comments: {
                    count: 1
                },
                likes: {
                    count: 24
                }
            },
        ]

        :param tags: str or tuple - hashtag (senza il #) o tupla di hastag
        :param count: int - limita i risultati
        :param top_posts: bool - limita ai top posts altrimenti ritorna tutto
        :param since: str - Risultati a partire da questa data, es. "20170101000000"
        :param until: str - Risultati entro questa data, es. "20171231235959"
        :return: list - lista di dizionari
        """
        if isinstance(tags, str):
            tags = (tags, )

        if since:
            try:
                since = datetime.strptime(since, "%Y%m%d%H%M%S")
            except ValueError:
                raise ValueError("Il parametro since non è in un formato corretto (es. '20170101000000')")

        if until:
            try:
                until = datetime.strptime(until, "%Y%m%d%H%M%S")
            except ValueError:
                raise ValueError("Il parametro until non è in un formato corretto (es. '20170101000000')")

        mapper = {
            'id': 'id',
            'comments': 'comments.count',
            'unix_datetime': 'date',
            'user': 'owner.id',
            'likes': 'likes.count',
            'is_video': 'is_video',
            'url': 'display_src',
            'height': 'dimensions.height',
            'width': 'dimensions.width',
            'caption': 'caption',
            'code': 'code'
        }

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
                res_media = res['tag']['top_posts']['nodes'] if top_posts else res['tag']['media']['nodes']
                has_next_page = res['tag']['media']['page_info']['has_next_page']

                # converto in oggetti SqlAlchemy
                sqlalchemy_media = []
                for element in res_media:

                    # Instagram non mi permette di cercare per data, però mi fornisce la
                    # data di creazione del post in formato Unix Timestamp. Quindi, per
                    # gestire il caso in cui volessi solo risultati in un certo intervallo,
                    # verifico che il mio post sia stato creato in questo lasso di tempo.

                    created_at = int(element['date'])
                    if since and created_at < time.mktime(since.timetuple()):
                        # sono andato troppo indietro, posso uscire
                        break
                    if until and created_at > time.mktime(until.timetuple()):
                        continue

                    model = Media()
                    for field_to, getter in mapper.items():
                        path = getter.split('.')
                        val = element
                        for key in path:
                            val = val.get(key, {})
                        if isinstance(val, dict):
                            val = None
                        setattr(model, field_to, val)
                    model.json = element
                    sqlalchemy_media.append(model)
                all_data_tag.extend(sqlalchemy_media)

                if res_media and has_next_page and not len(all_data_tag) > count and not top_posts:
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
        return all_data[:count]

    def get_by_media_codes(self, codes=(), all_comments=False, since=None, until=None):
        """
        Restituisce una lista contenente i dati dei post richiesti
        (identificati dalla stringa 'code' del post). Attivando
        il flag all_comments, verranno fatte ulteriori richieste
        gestendo la paginazione dei commenti. I commenti verranno
        aggiunti al json originale in modo da avere alla fina una
        lista composta da tanti elementi quanti sono i post
        richiesti.

        :param codes: stringa del codice o tupla con i codici dei post
        :param all_comments: bool - se attivato, scarica tutti i commenti
        :param since: str - Risultati a partire da questa data, es. "20170101000000"
        :param until: str - Risultati entro questa data, es. "20171231235959"
        :return: lista di json con i dati dei post richiesti
        """
        if isinstance(codes, str):
            codes = (codes,)

        if since:
            try:
                since = datetime.strptime(since, "%Y%m%d%H%M%S")
            except ValueError:
                raise ValueError("Il parametro since non è in un formato corretto (es. '20170101000000')")

        if until:
            try:
                until = datetime.strptime(until, "%Y%m%d%H%M%S")
            except ValueError:
                raise ValueError("Il parametro until non è in un formato corretto (es. '20170101000000')")

        all_data = []

        for code in codes:
            url = "{base}p/{code}?__a=1".format(
                base=self.base_url,
                code=code
            )
            res = requests.get(url)
            try:
                res = res.json()
            except Exception:
                raise PyInstagramException("Impossibile scaricare i dati dall'indirizzo: {}".format(url))

            # Instagram non mi permette di cercare per data, però mi fornisce la
            # data di creazione del post in formato Unix Timestamp. Quindi, per
            # gestire il caso in cui volessi solo risultati in un certo intervallo,
            # verifico che il mio post sia stato creato in questo lasso di tempo.

            created_at = int(res['graphql']['shortcode_media']['taken_at_timestamp'])
            if since and created_at < time.mktime(since.timetuple()):
                continue
            if until and created_at > time.mktime(until.timetuple()):
                continue

            if all_comments:
                while True:
                    page_info = res['graphql']['shortcode_media']['edge_media_to_comment']['page_info']
                    if page_info['has_next_page']:
                        next_url = url + "&max_id={}".format(page_info['end_cursor'])
                        next_res = requests.get(next_url)
                        next_res = next_res.json()
                        res_edges = res['graphql']['shortcode_media']['edge_media_to_comment']['edges']
                        next_edges = next_res['graphql']['shortcode_media']['edge_media_to_comment']['edges']
                        res_edges.extend(next_edges)
                    else:
                        break
            all_data.append(res)
        return all_data


