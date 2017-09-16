# -*- coding: utf-8 -*-
import requests


class OAuth(object):
    """
    Classe usata al fine di ottenere un access_token valido
    """

    _SCOPES = ("basic", "public_content", "follower_list", "comments", "relationships", "likes")

    def __init__(self, access_token=None, client_id=None, client_secret=None, authorization_redirect_uri=None, scopes=None):
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorization_redirect_uri = authorization_redirect_uri
        self.scopes = scopes or ("basic", )
        if any(scope not in self._SCOPES for scope in self.scopes):
            raise NameError("Non conosco tutti gli scope che hai passato!")

    def get_request_url(self):
        """
        Metodo usato per generare l'url usato per permettere a un utente di autorizzare l'app a usare il proprio
        profilo. Una volta ottenuta l'autorizzazione, Instagram opererà un redirect verso la pagina
        http://your-redirect-uri?code=CODE, dove la parte interessante ai fini di ottenere un access token valido
        sarà appunto la variabile CODE. Questo codice sarà poi il parametro obbligatorio usato dal metodo
        get_access_token.
        :return: str - Url di richiesta autorizzazione
        """
        if not all((self.client_id, self.authorization_redirect_uri)):
            raise Exception("OAuth non instaziata correttamente")
        request_url = "https://api.instagram.com/oauth/authorize/" \
                        "?client_id={CLIENTID}" \
                        "&redirect_uri={REDIRECTURI}" \
                        "&response_type=code" \
                        "&scope={SCOPES}".format(
                            CLIENTID=self.client_id,
                            REDIRECTURI=self.authorization_redirect_uri,
                            SCOPES='+'.join(self.scopes)
        )
        return request_url

    def get_access_token(self, code):
        """
        Metodo che setta l'access token, al seguito del quale sarà possibile iniziare a usare le API di Instagram.
        :param code:
        :return:
        """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': self.authorization_redirect_uri,
            'code': code,
        }
        response = requests.post('https://api.instagram.com/oauth/access_token', data=data)
        try:
            res_json = response.json()
            self.access_token = res_json['access_token']
        except Exception:
            raise Exception(response.text)
        else:
            return self.access_token
