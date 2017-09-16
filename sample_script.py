# -*- coding: utf-8 -*-

from datetime import datetime
from pyinstagram import OAuth, InstagramClient

CLIENT_ID = ""
CLIENT_SECRET = ""
REDIRECT_URI = ""

# AUTENTICAZIONE
auth = OAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorization_redirect_uri=REDIRECT_URI,
    scopes=("basic", "public_content")
)
print(auth.get_request_url())
code = input("Inserisci il codice ricevuto: ")
auth.get_access_token(code)
app = InstagramClient(auth)


# RECENT MEDIA - LAST 10
media = app.get_by_user()
for m in media[:10]:
    print(m.get('caption', {}).get('text', "Senza Titolo"))
    print("Postato il {}\n".format(datetime.fromtimestamp(
        int(m['created_time'])
    ).strftime('%Y-%m-%d %H:%M:%S')))


# SEARCH by HASHTAG
media = app.get_by_hashtag("salento")
for m in media:
    print(m['caption'].get('text'))
    print("Likes: {}".format(m['likes']['count']))
