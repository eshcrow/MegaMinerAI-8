#-*-python-*-
from BaseAI import BaseAI

import random

class AI(BaseAI):
  """The class implementing gameplay logic."""
  @staticmethod
  def username():
    return "Shell AI"

  @staticmethod
  def password():
    return "password"

  def init(self):
    print "Initializing"

  def end(self):
    pass

  def run(self):
  
    #----------------------------------------------------------------------
    #Pre-Defined Data Structures : 
    #vector of type Pirate  named pirates
    #vector of type Ship named ships
    #vector of type Port named ports
    #vector of type Tile named tiles
    #vector of type Treasure named treasures
    
    #If you need clarification on python, please find a dev
    #----------------------------------------------------------------------
    
    #----------------------------------------------------------------------
    #Port Functions:   
    #WHERE CALLING OBJECT IS A PORT
    
    #id()
      #Unique Identifier
    
    #x()
      #The X position of this object.  X is horizontal, with 0,0 as the top left corner
        
    #y()
      #The Y position of this object.  Y is vertical, with 0,0 as the top left corner
        
    #owner()
      #The owner of the port
    #----------------------------------------------------------------------
    
    #----------------------------------------------------------------------  
    #Pirate/Ship Functions:
    #WHERE CALLING OBJECT IS A PIRATE OR SHIP
    
    #id()
      #Unique Identifier
    
    #x()
      #The X position of this object.  X is horizontal, with 0,0 as the top left corner
    
    #y()
      #The Y position of this object.  Y is vertical, with 0,0 as the top left corner
    
    #owner()
      #The owner of the unit
    
    #health()
      #health of the unit
    
    #strength()
      #attacking strength of the unit
    
    #movesLeft()
      #Attacks left this turn for the unit
    
    #attacksLeft()
      #Moves left this turn for the unit
      
    #gold()
      #Amoutn of gold the unit is carrying
    #----------------------------------------------------------------------
    
    #----------------------------------------------------------------------
    #Tile Functions:
    #WHERE CALLING OBJECT IS OF TYPE TILE
    
    #id()
      #Unique Identifier
      
    #x()
      #The X position of this object.  X is horizontal, with 0,0 as the top left corner
      
    #y()
      #The Y position of this object.  Y is vertical, with 0,0 as the top left corner
      
    #type()
      #land = 0, water = 1
    #----------------------------------------------------------------------
    
    #----------------------------------------------------------------------  
    #Treasure Functions:
    #WHERE CALLING OBJECT IS OF TYPE TREASURE
    
    #id()
      #Unique Identifier

    #x()
      #The X position of this object.  X is horizontal, with 0,0 as the top left corner
      
    #y()
      #The Y position of this object.  Y is vertical, with 0,0 as the top left corner
    #----------------------------------------------------------------------
    
    #----------------------------------------------------------------------
    #Additional Functionality:
    
    
    #self.playerID()
      #Can be used to identify what player you are.

    #self.PirateCost()
      #Constant cost of a pirate unit

    #self.ShipCost()
      #Constant cost of a ship unit

    #self.PortCost()
      #Constant cost of a port

    #self.boardX()
      #The max length of the board's X

    #self.boardY()
      #The max length of the board's Y
      
    #self.getPath(startX, startY, endX, endY, tileType) 
      #Returns a vector of moves from the passed in start location to passed in end location over specified Tile type
      #0 = Land, 1 = Water. 
      #Example code provided in the snipets below
    #----------------------------------------------------------------------
  
    print "Turn:", self.turnNumber
    print "My ID: ", self.playerID()
    print "My Gold: ", self.players[self.playerID()].gold()

    #if you have enough gold to buy a pirate
    if self.pirateCost < self.players[self.playerID()].gold():
      #find a port you own
      for p in self.ports:
        if p.getOwner == self.playerID():
          p.createPirate()
          break

    #for each pirate in the world
    for i in self.pirates:
      #if I own the pirate
      if i.getOwner == self.playerID():
        #select a random pirate from the list
        target = random.choice(pirates)
        #Does a naive path finding algoritm that only takes into account tyle types, not other blocking problems
        #Takes a start x, start y, end x, end y, and a tile type on which you wish to path
        path = self.getPath(i.getX(), i.getY(), target.getX(), target.getY(), 0)
        #for all but the last step of the path, while I have steps, move
        for step in path:
          if i.getMovesLeft() <= 0:
            break
          i.move(step.getX(), step.getY())
        #get the distance between the guys
        distance = abs(i.getX() - target.getX()) + abs(i.getY() - target.getY())
        #If the distance is exactly 1 away and I don't own the guy
        if distance == 1 and i.getOwner() != target.getOwner():
          while i.getAttacksLeft() > 0:
           #attack the target
           i.attack(target)

    return 1

  def __init__(self, conn):
      BaseAI.__init__(self, conn)
