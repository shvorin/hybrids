What is hybrids
===============

This is a graphical chessboard (like XBoard) for the newly invented chess variant called 'hybrids'.
See README.rules to learn rules of this variant.

This project was started by me just to study python.  Piece images and some canvas are taken from
Jyrki Alakuijala's pythonchess (See http://freshmeat.net/projects/pythonchess/).

Dependencies
------------

 * Python (version 2.3 or 2.2 is OK)
 * Tkinter python library

Running the hybrids chessboard
------------------------------

Run the gboard.py executable in this directory (it may be necessary to chmod +x gboard.py):

    $ ./gboard.py

either call python explicitly:

    $ python gboard.py

What does it do?
----------------

gboard.py draws a chessboard with initial position.  It is possible to make moves by dragging pieces
(do moves for both sides).  Information about impossible moves goes to stdout.  Here are some hints
about making moves:
 * to form a hybrid just move a prime piece to another one of the same color (try to move the Rook from a1 to b1 at the initial position)
 * to dismiss a hybrid hit mouse pointer to the upper/lower third of the square where the hybrid is located and start to drag
 * to move the whole hybrid hit mouse pointer to the middle third of the square
 * en passant is possible :)
 * use left/right arrow keys to undo/redo; 'd' prints the current position in stdout; 'm' prints all legal moves

TODO
----

 * enable saving/loading games in PGN format
 * support ortodox variant
 * use more user-friendly way to draw hybrids
 * enable some king of networking: let gboard serves as a server and listens to clients (engines either other human players)
 * ...
 * enable other features that XBoard has
 * try to implement some engine for hybrids

Copyright
---------

This software is released under the GPL.
See http://www.gnu.org/copyleft/gpl.html for details.

Contact information
-------------------

Author:   Artem Shvorin
Email:    art@shvorin.net
Project homepage:
 * https://github.com/shvorin/hybrids
 * (obsolete) http://sourceforge.net/projects/hybrids/
