# Reversi
Author: Izakov Artemiy

Run command:
	python Reversi.py

Reversi is a strategy board game for two players, played on an uncheckered board.  
There are identical game pieces called disks, which are light on one side and dark on the other.  
Players take turns placing disks on the board with their assigned color facing up.  
During a play, any disks of the opponent's color that are in a straight line and bounded by the disk just placed and another disk of the   current player's color are turned over to the current player's color.

The object of the game is to have the majority of disks turned to display your color when the last playable empty square is filled.

---

Python recreation of classic game

Made for University course  
All pictures are drawn by me  
Using PyQt5 for GUI

Supports: 
 - Different sizes of board
 - Choosing your color
 - Passing your turn
 - Saving/Loading game on any step
 - Online mode
 - Different type of bot AI:
   - Easy - choses random possible place for a disk
   - Medium - choses best place for a disk for current moment
   - Hard - choses best place for a disk acording to all possible situations for several steps ahead
 - Possible places for a disk highlighting

Has 3 types of bots
