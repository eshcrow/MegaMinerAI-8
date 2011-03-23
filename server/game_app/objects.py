class Mappable:
  def __init__(self, game, id, x, y):
    self.game = game
    self.id = id
    self.x = x
    self.y = y

  def toList(self):
    value = [
      self.id,
      self.x,
      self.y,
      ]
    return value

  def nextTurn(self):
    pass

class Unit(Mappable):
  def __init__(self, game, id, x, y, owner, health, strength, hasMoved, hasAttacked):
    self.game = game
    self.id = id
    self.x = x
    self.y = y
    self.owner = owner
    self.health = health
    self.strength = strength
    self.hasMoved = hasMoved
    self.hasAttacked = hasAttacked

  def toList(self):
    value = [
      self.id,
      self.x,
      self.y,
      self.owner,
      self.health,
      self.strength,
      self.hasMoved,
      self.hasAttacked,
      ]
    return value

  def nextTurn(self):
    pass

  def move(self, x, y):
    print "Wrong move"
    return True

  def talk(self, message):
    self.game.animations.append(['talk', self.id, message])
    return true

  def _distance(self, x, y):
    distance = 0
    if self.x > x:
      distance += self.x - x
    elif  x > self.x:
      distance += x - self.x
    if self.y > y:
      distance += self.y - y
    elif y > self.y:
      distance += y - self.y
    return distance

  def _takeDamage(self, damage):
    self.health -= damage
    if self.health < 1 and self.id in self.game.objects:
      self.game.removeObject(self)

class Pirate(Unit):
  def __init__(self, game, id, x, y, owner, health, strength, hasMoved, hasAttacked):
    self.game = game
    self.id = id
    self.x = x
    self.y = y
    self.owner = owner
    self.health = health
    self.strength = strength
    self.hasMoved = hasMoved
    self.hasAttacked = hasAttacked

  def toList(self):
    value = [
      self.id,
      self.x,
      self.y,
      self.owner,
      self.health,
      self.strength,
      self.hasMoved,
      self.hasAttacked,
      ]
    return value

  @staticmethod
  def make(game, x, y, owner, health, strength):
    id = game.nextid
    game.nextid += 1
    # Placeholder for health and strength as 1, 1 respectively
    return Pirate(game, id, x, y, owner, health, strength, 0, 0)

  def nextTurn(self):
    self.hasMoved = 0
    self.hasAttacked = 0
    if self.game.playerID != self.owner:
      return True
    pass
    
  def takeDamage(self, pirate):
    self.health -= pirate.strength
    #If pirate is killed by the attack
    if self.health <= 0:  
      #If the pirate did not kill himself, transfer gold to killing pirate    
      if pirate.id != self.id:
        for i in self.game.objects.values():
          if isinstance(i,Treasure) and i.pirateID == self.id:
            i.pirateID = pirate.id
      #Otherwise the treasure becomes free game
      else:
        i.pirateID = -1
      self.game.removeObject(self)
    return True
          
      

  def move(self, x, y):
    #Checking to see if moving a valid piece
    if self.owner != self.game.playerID:
      return "Tried to move a unit that is not yours"  
 
    #Checks to see if the unit has moved this turn
    #0 if has not moved
    if self.hasMoved > 0:
      return "This unit has already moved this turn"
    
    #Makes sure the unit is only moving one space
    if self._distance(x,y) > 1:
      return "Cannot move that far!"  
   
    elif self._distance(x,y) == 0:
      return "Already at that location"  

    #Checking to make sure the unit is in the bounds of the map
    if x > self.game.boardX -1:
      return "Stepping off the world"
    elif y > self.game.boardY -1:
      return "Stepping off the world"
    elif y < 0:
      return "Stepping off the world"
    elif x < 0:
      return "Stepping off the world"

    #Check to see if the unit is moving into an enemy
    for i in self.game.objects.values():
      if isinstance(i,Unit):
        if i.owner != -1 and i.owner != self.owner and i.x == x and i.y == y:
          return "Enemy at that location"
      #Check to see if the unit is moving into an enemy port
      elif isinstance(i,Port):
        if i.owner != self.owner and i.x == x and i.y == y: 
          return "Moving into an enemy port"
      #Checking if unit is on land 
      elif isinstance(i,Tile):
        if i.x == x and i.y == y:
          isShip = False
          for j in self.game.objects.values():
            if isinstance(j,Ship):
  
              #-1 is placeholder value for neutral shop. May need to be changed
              if j.owner == self.owner or -1:
                isShip = True

          if i.type == 'w' and isShip != True:
            return "Pirates cannot swim!"

    #Lose control of ship if this is your last pirate leaving
    for i in self.game.objects.values():
      if isinstance(i,Ship) and i.x == x and i.y == y:
        if i.owner == self.owner:
          counter = 0
          #if the pirate was on a ship, count how many pirates are on it
          for j in self.game.objects.values():
            if isinstance(j,Pirate) and j.x == x and j.y ==y:
              counter+=1
          #If this was the last pirate on board, the ship becomes neutral.
          if counter == 1:
            i.owner = -1          
            
    #Moves the unit and makes it unable to move until next turn
    self.hasMoved += 1
    self.x = x
    self.y = y
    #self.game.animations.append(['move', self.id, d])
    
    #Take control of a ship if you are the first one on it
    for i in self.game.objects.values():
      if isinstance(i,Ship) and i.x == x and i.y == y:
        if i.owner == -1:
          i.owner = self.owner

    #Moves the treasure this pirate is carrying to the new location
    for i in self.game.objects.values():
      if isinstance(i,Treasure):
        if self.id == i.pirateID:
          i.x = x
          i.y = y
    
    return True

  def talk(self, message):
    pass


  def pickupTreasure(self, amount):
    for i in self.game.objects.values():
      if isinstance(i,Treasure):
        if i.x == self.x and i.y == self.y and i.pirateID == -1:
          #Pirate picks up all of the treasure
          if amount == i.amount:
            i.pirateID = self.ID
          #Pirate picks up a portion of the treasure
          elif amount < i.amount:
            i.amount -= amount
            treasure = i.make(game,self.x,self.y,self.ID,amount)
            game.addObject(treasure)
          #Pirate tries to pick up more treasure than allowed
          else:
            return "There isn't that much treasure!"
    return True


  def dropTreasure(self, amount):   
    for i in self.game.objects.values():
      if isinstance(i,Treasure):
        #Locates the treasure being modified
        if i.pirateID == self.ID:
          if amount > i.amount:
             return "Not that much gold to drop"
          for j in self.game.objects.values():
            #if the treasure is being dropped on a port
            if isinstance(j,Port):
              if i.x == j.x and i.y == j.y:
                #Increase gold of owner
                if self.owner == 0:
                  self.game.player0Gold += i.amount
                else:
                  self.game.player1Gold += i.amount
                #Decrement gold if only partially dropped
                if amount < i.amount:
                  i.amount -= amount
                #Remove if all dropped
                else:
                  self.game.removeObject(self.game.objects[i])
                return True
            #If there is already treasure at this location
            elif isinstance(j,Treasure):
              if i.x == j.x and i.y == j.y and i.id != j.id:
                #If they drop all of their treasure, remove the original
                #from the game
                #Else, simply increment the treasure on the ground and 
                #decrement that which the pirate is holding
                j.amount += i.amount
                if amount < i.amount:
                  i.amount -= amount                
                if amount == i.amount:
                  self.game.removeObject(self.game.objects[i])
          #If there was no previous treasure and there is no port          
          #If they dropped all of their trasure simply change owner to neutral
          if amount == i.amount:         
            i.pirateID = -1    
          #Dropping only a portion of their gold  
          #Decrement pirate's treasure amount, then create a new neutral treasure
          #at this location          
          else:
            i.amount -= amount
            treasure = i.make(game,self.x,self.y,-1,amount)
            game.addObject(treasure)
    return True
                      
  def buildPort(self):
    for i in self.game.objects.values():
      if isinstance(i, Tile):
        if i._distance(self.x,self.y) == 1: #Not sure about this
          if i.type == 1:
            if self.onwer == 0:
              if game.self.player0Gold >= portCost:
                game.self.player0Gold -= portCost
                port = i.make(game,self.x,self.y,self.owner)
                game.addObject(port)
                return True
              else:
                return "Not enough gold to make this purchase"
            else:
              if game.self.player1Gold >= portCost:
                game.self.player1Gold -= portCost
                port = i.make(game,self.x,self.y,self.owner)
                game.addObject(port)
                return True
              else:
                return "Not enough gold to make this purchase"
          else:
           return "No water connected to this location"
    return True
  #TODO: Test and review this logic

  def attack(self, Target):
    #Make sure you own the attacking unit
    if self.owner != self.game.playerID:
      return "This be not yarr ship, ye swine!"
     
    #Checks to see that the target is in range     
    if self._distance(Target.x,Target.y) > 1:
      return "That target is not in your range"      
      
    #Makes sure the opponent's type is ship
    if isinstance(Target,Pirate) == false:
      return "You may only attack pirates with your pirates"
      
    #Meets all conditions for attack
    self.hasAttacked += 1    
    Target.takeDamage(self)
    return True
    
class Port(Mappable):
  def __init__(self, game, id, x, y, owner):
    self.game = game
    self.id = id
    self.x = x
    self.y = y
    self.owner = owner

  def toList(self):
    value = [
      self.id,
      self.x,
      self.y,
      self.owner,
      ]
    return value

  @staticmethod
  def make(game, x, y, owner):
    id = game.nextid
    game.nextid += 1
    return Port(game, id, x, y, owner)
    
  def nextTurn(self):
    #TODO: Hits every enemy unit round the port for half of its max health
    pass

        
    

  def createPirate(self):
    #Decrememnting gold of corresponding player
    if self.owner == 0:
      if player0Gold >= pirateCost:
        player0Gold -= pirateCost
      else:
        return "Not enough gold for that unit"
    else:
      if player1Gold >= pirateCost:
        player1Gold -= pirateCost
      else:
        return "Not enough gold for that unit"
    pirate = pirate.make(game, self.x, self.y, self.owner, 10, 2) #placeholder values
    game.addObject(pirate)
    return True
  #TODO: Test and review this logic

  def createShip(self):
    #Decrememnting gold of corresponding player
    if self.owner == 0:
      if player0Gold >= shipCost:
        player0Gold -= shipCost
      else:
        return "Not enough gold for that unit"
    else:
      if player1Gold >= shipCost:
        player1Gold -= shipCost
      else:
        return "Not enough gold for that unit"
    #Checks to make sure there is no other ships in the port
    for i in self.game.objects.values():
      if isinstance(i,Ship) and i.x == self.x and i.y == self.y:
        return "There is already a ship in the port"      
    pirate = pirate.make(game, self.x, self.y, self.owner, 10, 2) #placeholder values
    game.addObject(pirate)
    return True    
    pass



class Ship(Unit):
  def __init__(self, game, id, x, y, owner, health, strength, hasMoved, hasAttacked):
    self.game = game
    self.id = id
    self.x = x
    self.y = y
    self.owner = owner
    self.health = health
    self.strength = strength
    self.hasMoved = hasMoved
    self.hasAttacked = hasAttacked


  def toList(self):
    value = [
      self.id,
      self.x,
      self.y,
      self.owner,
      self.health,
      self.strength,
      self.hasMoved,
      self.hasAttacked,
      ]
    return value
    
  @staticmethod
  def make(game, x, y, owner, health, strength):
    id = game.nextid
    game.nextid += 1
    # Placeholder for health and strength as 1, 1 respectively
    return Ship(game, id, x, y, owner, health, strength, 0, 0)
  
  def nextTurn(self):
    pass

  def move(self, x, y):
    #Check the owner of the ship before moving
    if self.owner != self.game.playerID:
      return "This be not yarr ship, ye swine!"
      
    if self.hasMoved != 0:
      return "This ship has already moved this turn" 
     
    if self._distance(x,y) > 1:
      return "Cannot move that far!"
   
    elif self._distance(x,y) == 0:
      return "Already at that location"
    
    #Checking the bounds of the map
    if x > self.game.boardX -1:
      return "Stepping off the world"
    elif y > self.game.boardY -1:
      return "Stepping off the world"
    elif y < 0:
      return "Stepping off the world"
    elif x < 0:
      return "Stepping off the world" 
     
    #Makes sure the ship stays on water
    for i in self.game.objects.values():
      if isinstance(i,Tile) and i.x == x and i.y == y:
        if i.type != 1:
          return "Ships cannot walk!"
      
    #Makes sure there is no units at target location
    for i in self.game.objects.values():
      if isinstance(i,Unit):
        if i.x == x and i.y == y:
          return "There is already a unit at that location"  

    #Ship has passed all checks and it ready to move
    self.hasMoved += 1
    
    #Moving all treasure,pirates on the ship to the new location
    #Also moves the ship to the new location
    for i in self.game.objects.values():
      if isinstance(i,Pirate) and i.x == x and i.y == y:
        i.x = x
        i.y = y
      elif isinstance(i,Treasure) and i.x == x and i.y == y:
        i.x = x
        i.y = y
      elif isinstance(i,Ship) and i.x == x and i.y == y:
        i.x = x
        i.y = y
    return True
    
  def talk(self, message):
    pass

  def attack(self, Target):
    #Make sure you own the attacking unit
    if self.owner != self.game.playerID:
      return "This be not yarr ship, ye swine!"
     
    #Checks to see that the target is in range     
    if self._distance(Target.x,Target.y) > 2:
      return "That target is not in your range"      
      
    #Makes sure the opponent's type is ship
    if isinstance(Target,Ship) == false:
      return "You may only attack ships with your ship"
      
    #Meets all conditions for attack
    self.hasAttacked += 1    
    Target.takeDamage(self.strength)
    return True
    
  def takeDamage(self, strength):
    self.health -= strength   
    #If the ship is killed by the attack
    #Destroy everything that was on it
    if self.health <= 0:
      for i in selg.game.objects.values():
        if i.x == self.x and i.y == self.y:
          self.game.removeObject(self)
    return True          

class Tile(Mappable):
  def __init__(self, game, id, x, y, type):
    self.game = game
    self.id = id
    self.x = x
    self.y = y
    self.type = type #1 for water, 0 for land

  def toList(self):
    value = [
      self.id,
      self.x,
      self.y,
      self.type,
      ]
    return value
  
  def _distance(self, x, y):
    distance = 0
    if self.x > x:
      distance += self.x - x
    elif  x > self.x:
      distance += x - self.x
    if self.y > y:
      distance += self.y - y
    elif y > self.y:
      distance += y - self.y
    return distance

  @staticmethod
  def make(game, x, y, type):
    id = game.nextid
    game.nextid += 1
    #1 is water, 0 is land
    return Tile(game, id, x, y, type)
  
  def nextTurn(self):
    pass



class Treasure(Mappable):
  def __init__(self, game, id, x, y, pirateID, amount):
    self.game = game
    self.id = id
    self.x = x
    self.y = y
    self.pirateID = pirateID
    self.amount = amount 

  def toList(self):
    value = [
      self.id,
      self.x,
      self.y,
      self.pirateID,
      self.amount,
      ]
    return value
  
  @staticmethod
  def make(game, x, y, pirateID, amount):
    id = game.nextid
    game.nextid += 1
    return Treasure(game, id, x, y, pirateID, amount)
  
  def nextTurn(self):
    pass
