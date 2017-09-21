# -*- coding: utf-8 -*-

from datetime import datetime
from pprint import pprint

from pyinstagram import OAuth, InstagramApiClient, InstagramJsonClient

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
app = InstagramApiClient(auth)


# RECENT MEDIA - LAST 10
media = app.get_by_user(count=3)
for m in media:
    print(m.get('caption', {}).get('text', "Senza Titolo"))
    print("Postato il {}\n".format(datetime.fromtimestamp(
        int(m['created_time'])
    ).strftime('%Y-%m-%d %H:%M:%S')))

# SEARCH by HASHTAG
media = app.get_by_hashtag("salento")
for m in media:
    print(m['caption'].get('text'))
    print("Likes: {}".format(m['likes']['count']))

tags = app.search_for_tag("developer", count=3)
for tag, count in tags.items():
    print("{0}\t{1}".format(tag, count))

app = InstagramJsonClient()
media = app.get_by_user("nasa")

print("L'utente {utente} ha postato {count} media (immagini o video).".format(
    utente=next(iter(media), {}).get('user', {}).get('full_name', "maxmara"),
    count=len(media)
))
print("Numero totale di likes: {}".format(
    sum(m['likes']['count'] for m in media)
))

app = InstagramJsonClient()
media = app.get_by_user("cern", count=1)
pprint(media[0])

media = app.get_by_hashtag("milanofashionweek")
for m in media:
    print(m['display_src'])

app = InstagramJsonClient()
media = app.get_by_hashtag("mfw", count=1, top_posts=False)[0]
print(media.caption)
print(media.created_at)
print(media.code)
pprint(app.get_by_media_codes(media.code))


