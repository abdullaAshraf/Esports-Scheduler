class Player:
    id = ""
    owned = 0
    points = 0
    games = 0
    price = 0

    def __init__(self,id,owned,points,games,price):
        self.id = id
        self.owned = owned
        self.points = points
        self.games = games
        self.price = price