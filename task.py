import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from datetime import timedelta
import json
import os

from player import Player

os.environ["private_key_id"] = "74c849eea120db1d6e2f8ac5cbdf4ee29b2b3555"
os.environ["private_key"] = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDZQ65ZYJw0ydZw\nkLQIKVQ84e5v3imY6WcG4bRlWKRJ+8kBp7le4Fhhpdg/HqI538/dCK6BOVwj9V0u\n62zfCVUAQCCLo7jRSIwjn/E68gApBk8uNQ6LeunwHlPv3SFeZKAdLZqEals3myRW\nQrdhOtKuMdDvLyfrxbZVRhk7JdqkEhaxsBZQpQQ+gi7TP87tz85z+GoUlkLTo4yp\n8G3DtSQAfhHr4rznaSbc8e/vstMqZRX6fo+xLx3j9t/cc8Se13/9iQpnAdhcJiYJ\n0wgc0a1m/wE1voU3OC46BBarWt6O7SsoxY3+K3DNAYy9rm6xdrg0TnNhx+S3Efyu\nzjsQdO8NAgMBAAECgf9rsAPXZZmVdDyc4//mRJXuCSqXnYZWC5MFZGg+twZFpWqm\nvLR6GWN8WEW6ka1lOxg+PZ2Wb4KRbJrDUXvBgt6ez2MZYdQ5dbwAXioW1IcG6v03\nsRSg8WfmRyH+M9Wrnm2FXjGqGw1USZGATHTRSsh3juQ5cLRY0zTiK9yOkRg/x80N\nbSs9gHHmCrCJ0ZXXm41jm+TZzFgtjSjqLeRq3ndQo7bzogj7hxeZL1NWsbL2311+\nPMGBhTV8mkrb6ZZjo9sLXKyY2VbnxLPg6BXn6R7ns40uwmXUxJvAvbA0PfHwzc9Y\nrSSYZTDzXdS2wT90+7yNcNXl++iNhbRuW0hNcCkCgYEA/bgAOXoj9cyWcDgpW+gK\n72oAuxF6xe2jS3Pbh1AdyhuEfzHLGAdDoLWn72UjXCOONoWSgooapfFL2SQfOmuw\nlu34ge898TEidEtgkz5ct/Zn+0B8Uu3bIHIJ9kAhJdIHKJM1ZJ4X8Rh2gUm9Ts4N\n4jY92pSzAkMbuUKeTEL5GOMCgYEA2zfFYnEsDzTcqM/c0BBdLqAPGTyqySno7qxu\nSMc9PxJEnBHv/jKgN6oXt8BSMODsLS2KtVkvRX7t01nEK+OPxoDHWXmftz5MqtWm\n+/jql+KaIxwVws318kdFrYgPRvC9RC+01akwn4L/YV8Ig+NkL7MPJDjSeOhVPT1v\nueoRi08CgYEA2Fkqd9ibCWIndhGt0t0PVhACB4JkOprk/9YPgFbk0A6e8Qc4s4ie\nNlAwn4aSnGMFRaCoyf+RsacMkmCm8F4b+td5bPLg0uafBqOv+l7XGVdYW3sliGGi\n1QvpSr5shZ+O0x6UDPRyXfgKNTz33FcAp8CxBc5+xpMK9PLFoSoK1xkCgYEArYvC\ndMOZmNRFmFMuwX0i9+V47obLwgOuxzy09mLdBtCEhnXg5AHaOxcqPatApjd6Ye26\n8QSQ2ti4mOho2EIIMaMDrr8NhTkJ4vjPgI0301RuqDr0s0rwWYS5Eb80MPonLBME\ne129A5rmaISeriLXzrdX1loxrcxoptm7WJiImRsCgYEAyBHGVvwpyqzCWIOz7ei5\nliYRVvTeyQVVUypPO9hDP+E/j61Ocp5Z4Phx8LLzifTNIB8A/jHnD6yMrUTN0HyS\nsxaO5EN7JJZHLa2sX/erb2MbvxC1jpvK6BwT9Z/0no1qNYO4+yb0pOqlWSSDdTPH\nvVzNyobD3mF6LQ+3WaMdi+0=\n-----END PRIVATE KEY-----\n"
os.environ["client_email"] = "firebase-adminsdk-7r02q@esports-lol.iam.gserviceaccount.com"
os.environ["client_id"] = "112852782137790085824"

players = {}

def setupFirebase():
    if not os.path.isfile('./serviceAccountKey.json'):
        credObject = {
            "type": "service_account",
            "project_id": "esports-lol",
            "private_key_id": os.environ['private_key_id'],
            "private_key": os.environ['private_key'],
            "client_email": os.environ['client_email'],
            "client_id": os.environ['client_id'],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": u"https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-7r02q%40esports-lol.iam.gserviceaccount.com"
        }
        with open('./serviceAccountKey.json', 'w') as outfile:
            json.dump(credObject, outfile)
    cred = credentials.Certificate("./serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db
    
def updatePlayers() -> bool:
    db = setupFirebase()

    #get last update timestamp
    doc = db.collection(u'global').document(u'lastPlayersUpdate')
    docDict = doc.get().to_dict()
    timestamp = docDict['time']
    maxPoints = docDict['maxPoints']

    try:
        timestamp = datetime.strptime(''.join(str(timestamp).rsplit(':', 1)), "%Y-%m-%d %H:%M:%S.%f%z")
    except Exception as e:
        if type(e) is ValueError:
            timestamp = datetime.strptime(''.join(str(timestamp).rsplit(':', 1)), "%Y-%m-%d %H:%M:%S%z")
        else :
            print(e)

    cnt = 0
    #get all games from timestamp up to now
    while True:
        oldTimestamp = timestamp
        timestamp,cnt = getNextGamesPatch(timestamp,cnt)
        if oldTimestamp == timestamp:
            break
    
    #add 1 second to avoid this timestamp later
    timestamp += timedelta(seconds=1)

    updatePlayersIDs()
    
    #fix changed and missing tags
    for id in list(players):
        if players[id].id == "":
            newId , fullId = getPlayerNewID(id)
            if(newId != None):
                if newId in players:
                    players[newId].merge(players[id])
                else:
                    players[newId] = players[id]
                    players[newId].id = fullId
            del players[id]

    playersCollection = db.collection(u'players')


    for player in players:
        playerDict = playersCollection.document(players[player].id).get().to_dict()
        if playerDict != None:
            players[player].games += playerDict['games']
            players[player].points += playerDict['points']
            playersCollection.document(players[player].id).set(players[player].getData(),{'merge': True})
        else:
            playersCollection.document(players[player].id).set({'points' : players[player].points, 'games' : players[player].games, 'owned' : 0})
        maxPoints = max(maxPoints,players[player].ptsGame())
        
    doc.update({'time': timestamp , 'maxPoints': maxPoints})

    return True

def getPlayerNewID(id):
    data = requests.get(f'https://esports.now.sh/Player/{id}').json()
    if len(data) > 0:
        player = data[0]['title']
        return player['Page'] , f"{player['ID']}({player['Name']})"
    return None , None

def updatePlayersIDs():
    data = requests.get('https://esports.now.sh/Players').json()
    for player in data:
        if player['Page'] in players:
            players[player['Page']].id = f"{player['ID']}({player['Name']})"

def getNextGamesPatch(timestamp, ignore) -> datetime:
    #get data from API
    data = getData(timestamp)

    if len(data) == 0:
        return timestamp,0

    newTimestamp = data[-1]['title']['DateTime UTC']
    cnt = 0

    for gameRecord in data:
        if ignore > 0:
            ignore -=1
            continue
        game = gameRecord['title']
        if game['Link'] not in players:
            players[game['Link']] = Player()
        players[game['Link']].addGame(game)
        if game['DateTime UTC'] == newTimestamp:
            cnt += 1

    return datetime.strptime(newTimestamp,"%Y-%m-%d %H:%M:%S") , cnt


def getData(timestamp):
    return requests.get('https://esports.now.sh/Game/' + timestamp.strftime("%Y-%m-%d %H:%M:%S")).json()

if __name__ == "__main__":
    updatePlayers()

