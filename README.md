# PyInstagram

[![license](https://img.shields.io/github/license/mashape/apistatus.svg)]()
[![python](https://img.shields.io/badge/python-3.6-orange.svg)]()

PyInstagram è una libreria creata con lo scopo di semplificare l'integrazione delle API di Instagram in un progetto Python. Si compone di due classi principali:

  - **OAuth**: per la gestione dell'autenticazione al fine di ottenere un access token
  - **InstagramClient**: che si occupa di fare le chiamate all'API con lo scopo di restituire i dati da Instagram in un formato "pythonico"

# Nuove Funzionalità!

  - Ricerca post recenti per nomeutente
  - Ricerca post per hashtag
  - Ricerca hashtag simili (in base al numero di post)


## Installazione

PyInstagram è stata scritta usando [Python 3](https://www.python.org/).

Per installarla, lancia il seguente comando:

```sh
$ pip install git+https://github.com/alessandrocucci/PyInstagram.git
```

## Utilizzo
### Autenticazione
Dopo aver creato una app Instagram ([https://www.instagram.com/developer/](https://www.instagram.com/developer/)), le informazioni che ci servono sono:
- id_client
- client_secret
- url di redirect

Lo scopo delle seguenti righe sarà quello di ottenere un access token valido da usare per fare le nostre richieste verso le Instagram API:

```python
from pyinstagram import OAuth

CLIENT_ID = "ilClientID"
CLIENT_SECRET = "laNostraChiaveSecret"
REDIRECT_URI = "http://ilNostroUri"

auth = OAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorization_redirect_uri=REDIRECT_URI,
    scopes=("basic", "public_content")
)

print(auth.get_request_url())
code = input("Inserisci il codice ricevuto: ")
auth.get_access_token(code)
```
Eseguendo questo script da terminale troverete un link 
come questo e un prompt che attende l'inserimento di un codice:
```
https://api.instagram.com/oauth/authorize/?client_id=ilClientID&redirect_uri=http://ilNostroUri&response_type=code&scope=basic+public_content
Inserisci il codice ricevuto:
```
Visitando il link nel browser, Instagram vi chiederà di loggarvi e se autorizzare l'uso dell'applicazione. 
Una volta acconsentito, verremo reindirizzati a un link del tipo http://ilNostroUri?code=34873627498476284943

Quello che dovremo fare, sarà copiare il codice generato (quello dopo 'code='), e incollarlo nel programma, che nel frattempo è li in attesa. Se tutto va a buon fine, 
l'oggetto auth avrà tutti gli attributi settati per permetterci di dialogare con le API di Instagram, e ottenere i dati che ci servono.

### Struttura degli oggetti delle risposte
Quasi tutti i metodi in get di InstagramClient restituiscono una lista (o un'eccezione se qualcosa va storto) di dizionari fatti in questo modo:

```python
[{'caption': {'created_time': '1296710352',
              'from': {'full_name': 'Kevin Systrom',
                       'id': '3',
                       'type': 'user',
                       'username': 'kevin'},
              'id': '26621408',
              'text': 'Inside le truc #foodtruck'},
  'comments': {'count': 0},
  'created_time': '1296710327',
  'filter': 'Earlybird',
  'id': '22721881',
  'images': {
    'low_resolution': {'height': 306,
                       'url': 'http://distillery.s3.amazonaws.com/[...].jpg',
                       'width': 306},
    'standard_resolution': {'height': 612,
                            'url': 'http://distillery.s3.amazonaws.com/[...].jpg',
                            'width': 612},
    'thumbnail': {'height': 150,
                  'url': 'http://distillery.s3.amazonaws.com/[...].jpg',
                  'width': 150}},
  'likes': {'count': 15},
  'link': 'http://instagr.am/p/BWrVZ/',
  'location': {'id': '520640',
               'latitude': 37.77872018361018,
               'longitude': -122.3962783813477,
               'name': 'Le Truc',
               'street_address': ''},
  'tags': ['foodtruck'],
  'type': 'image',
  'user': {'id': '3',
           'profile_picture': 'http://distillery.s3.amazonaws.com/[...].jpg',
           'username': 'kevin'},
  'users_in_photo': []}]
```
E adesso, un po' di esempi di utilizzo della libreria vera e propria:

### Post recenti della NASA
NB. Questo necessita un'app che non sia in modalità Sandbox 
(a meno che non siate voi stessi i proprietari dell'account della Nasa...)

```python
from datetime import datetime

from pyinstagram import InstagramClient
app = InstagramClient(auth)

media = app.get_by_user("nasa")
for m in media:
    print(m.get('caption', {}).get('text', "Senza Titolo"))
    print("Postato il {}\n".format(datetime.fromtimestamp(
        int(m['created_time'])
    ).strftime('%Y-%m-%d %H:%M:%S')))
```

### Gli ultimi 10 post pubblicati 
###### (dall'utente che ha autorizzato l'uso dell'applicazione)
```python
from datetime import datetime

from pyinstagram import InstagramClient
app = InstagramClient(auth)

media = app.get_by_user(count=10)
for m in media:
    print(m.get('caption', {}).get('text', "Senza Titolo"))
    print("Postato il {}\n".format(datetime.fromtimestamp(
        int(m['created_time'])
    ).strftime('%Y-%m-%d %H:%M:%S')))
```

### Ricerca per hashtag
```python
media = app.get_by_hashtag("salento")
for m in media:
    print(m['caption'].get('text'))
    print("Likes: {}".format(m['likes']['count']))
```

### Ricerca di hashtag simili, in base al numero di post

```python
tags = app.search_for_tag("python", count=3)
print(tags)
```

## Development

Vuoi darmi una mano a completarne lo sviluppo? Eccellente!

Forka il repository, scrivi le tue modifiche, e mandami una Pull Request.

## Todo

 - Trasformare tutti gli endpoint in oggetti SqlAlchemy
 - Gestire il caso in cui un access token scada
 - Aggiungere ricerca per geolocalizzazione
 - Aggiungere filtri per min_id e max_id
 - Scrivere integration test
 - Scrivere documentazione
 - Se tutto va come deve, scrivere i metodi per le richieste in push, in modo da poter usare questa libreria anche per eventuali bots.

Licenza
----

MIT
