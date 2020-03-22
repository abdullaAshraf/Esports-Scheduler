import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from datetime import timedelta
import json
import os

from player import Player

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

