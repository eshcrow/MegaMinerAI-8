// -*-c++-*-

#ifndef UNIT_H
#define UNIT_H

#include <iostream>
#include "structures.h"

#include "Mappable.h"
class Unit;

///Generic Unit
class Unit : public Mappable {
  public:
  Unit(_Unit* ptr = NULL);

  // Accessors
  ///Unique Identifier
  int id();
  ///The X position of this object.  X is horizontal, with 0,0 as the top left corner
  int x();
  ///The Y position of this object.  Y is vertical, with 0,0 as the top left corner
  int y();
  ///The owner of the unit
  int owner();
  ///Health of the unit
  int health();
  ///Attacking strength of the unit
  int strength();
  ///Displays the remaining moves for this unit this turn
  int movesLeft();
  ///Displays the remaining attacks for this unit this turn
  int attacksLeft();
  ///Amount of gold carried by the unit.
  int gold();

  // Actions
  ///Move the unit to the designated X and Y coordinates
  int move(int x, int y);
  ///Allows a unit to display a message to the screen.
  int talk(char* message);
  ///Attempt to attack the given unit
  int attack(Unit& Target);

  // Properties


  friend std::ostream& operator<<(std::ostream& stream, Unit ob);
};

#endif

