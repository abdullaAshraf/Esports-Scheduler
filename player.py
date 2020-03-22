class Player:
    id = ""
    points = 0
    games = 0

    def addGame(self,game):
        self.games += 1
        self.points += calculatePoints(game)

    def ptsGame(self):
        return self.points / self.games

    def getData(self):
        return {'points' : self.points, 'games' : self.games}

    def print(self):
        print(f'{self.id} : {self.games} - {self.points}')

    def merge(self,player):
        self.points += player.points
        self.games += player.games
        
def calculatePoints(game) -> float:
    points = 0
    points += 3 * int(game['Kills'])
    points -= 1 * int(game['Deaths'])
    points += 1.5 * int(game['Assists'])
    points += 0.02 * int(game['CS'])

    if (int(game['Kills']) + int(game['Assists']) >= 10):
        points += 3

    if (game['PlayerWin'] == 'Yes'):
        if (float(game['Gamelength Number']) <= 20):
            points += 5
        elif (float(game['Gamelength Number']) <= 30):
            points += 3
        else:
            points += 2
    
    return points